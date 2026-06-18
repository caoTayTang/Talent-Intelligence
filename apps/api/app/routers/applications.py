from uuid import UUID
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from talent_core.db import get_db
from talent_core.models import Application, ApplicationStatus
from app.queue import enqueue
from app.schemas.applications import (
    CreateApplicationRequest,
    SubmitTestRequest,
    ApplicationResponse,
    PaginatedApplicationsResponse
)

from typing import List as PyList

router = APIRouter()


@router.get("", response_model=PaginatedApplicationsResponse)
def list_applications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> PaginatedApplicationsResponse:
    total = db.query(Application).count()
    apps = db.query(Application).order_by(Application.created_at.desc()).offset(skip).limit(limit).all()
    return PaginatedApplicationsResponse(
        items=[ApplicationResponse.from_model(a) for a in apps],
        total=total
    )


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    request: CreateApplicationRequest, db: Session = Depends(get_db)
) -> ApplicationResponse:
    # Check if application already exists
    existing = db.query(Application).filter(
        Application.candidate_id == request.candidate_id,
        Application.job_id == request.job_id
    ).first()

    if existing:
        return JSONResponse(
            status_code=409,
            content={
                "detail": "You have already applied for this job.",
                "existing_id": str(existing.id)
            },
            headers={"X-Existing-ID": str(existing.id)}
        )

    application = Application(
        candidate_id=request.candidate_id,
        job_id=request.job_id,
        cv_object_key=request.cv_object_key,
        status=ApplicationStatus.pending_cv,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    enqueue("agent.cv_screening", {"application_id": str(application.id)})

    return ApplicationResponse.from_model(application)


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID, 
    request: CreateApplicationRequest, 
    db: Session = Depends(get_db)
) -> ApplicationResponse:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update CV and reset status for re-screening
    application.cv_object_key = request.cv_object_key
    application.status = ApplicationStatus.pending_cv
    application.cv_score = None
    application.detailed_score_json = None
    application.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(application)

    enqueue("agent.cv_screening", {"application_id": str(application.id)})

    return ApplicationResponse.from_model(application)


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID, db: Session = Depends(get_db)
) -> ApplicationResponse:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return ApplicationResponse.from_model(application)


@router.post("/{application_id}/submit-test", response_model=ApplicationResponse)
def submit_test(
    application_id: UUID, request: SubmitTestRequest, db: Session = Depends(get_db)
) -> ApplicationResponse:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    application.test_answer = request.test_answer
    application.test_submission_url = request.test_submission_url
    application.status = ApplicationStatus.test_submitted
    db.commit()

    enqueue("agent.assessment", {"application_id": str(application.id)})
    return ApplicationResponse.from_model(application)
