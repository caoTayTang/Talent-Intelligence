from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from talent_core.db import get_db
from talent_core.models import Application, ApplicationStatus
from app.queue import enqueue
from app.schemas.applications import (
    CreateApplicationRequest,
    SubmitTestRequest,
    ApplicationResponse,
)

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    request: CreateApplicationRequest, db: Session = Depends(get_db)
) -> ApplicationResponse:

    application = Application(
        candidate_id=request.candidate_id,
        job_id=request.job_id,
        cv_object_key=request.cv_object_key,
        status=ApplicationStatus.pending_cv,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # Enqueue background job to process CV, will failed cause i comment the TASK_TO_QUEUE
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
