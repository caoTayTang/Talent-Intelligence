from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from talent_core.db import get_db
from talent_core.models import Job
from app.schemas.jobs import (
    CreateJobRequest,
    JobResponse,
)

router = APIRouter()


@router.post("", response_model=JobResponse, status_code=201)
def create_job(request: CreateJobRequest, db: Session = Depends(get_db)) -> JobResponse:

    job = Job(
        company_id=request.company_id,
        title=request.title,
        description=request.description,
        test_content=request.test_content,
        test_object_url=request.test_object_url,
        scorecard_json=request.scorecard_json,
        jd_object_url=request.jd_object_url,
        is_active=request.is_active,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobResponse.from_model(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> JobResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse.from_model(job)

