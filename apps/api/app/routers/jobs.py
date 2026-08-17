from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from talent_core.db import get_db
from talent_core.models import Job
from app.schemas.jobs import (
    CreateJobRequest,
    JobResponse,
    PaginatedJobsResponse
)
from app.queue import enqueue

from typing import List as PyList

router = APIRouter()


@router.get("", response_model=PaginatedJobsResponse)
def list_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> PaginatedJobsResponse:
    total = db.query(Job).count()
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return PaginatedJobsResponse(
        items=[JobResponse.from_model(j) for j in jobs],
        total=total
    )


@router.post("", response_model=JobResponse, status_code=201)
def create_job(request: CreateJobRequest, db: Session = Depends(get_db)) -> JobResponse:

    job = Job(
        company_id=request.company_id,
        title=request.title,
        description=request.description,
        test_mode=request.test_mode,
        test_content=request.test_content,
        test_object_url=request.test_object_url,
        scorecard_json=request.scorecard_json,
        jd_object_url=request.jd_object_url,
        cv_submission_deadline=request.cv_submission_deadline,
        test_start_date=request.test_start_date,
        test_end_date=request.test_end_date,
        interview_start_date=request.interview_start_date,
        interview_end_date=request.interview_end_date,
        result_announcement_date=request.result_announcement_date,
        cv_pass_quota=request.cv_pass_quota,
        assessment_pass_quota=request.assessment_pass_quota,
        interview_pass_quota=request.interview_pass_quota,
        is_active=request.is_active,
        dynamic_test_config=request.dynamic_test_config.model_dump() if request.dynamic_test_config else None,
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


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: UUID, 
    request: CreateJobRequest, 
    db: Session = Depends(get_db)
) -> JobResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job.title = request.title
    job.description = request.description
    job.test_mode = request.test_mode
    job.test_content = request.test_content
    job.test_object_url = request.test_object_url
    job.scorecard_json = request.scorecard_json
    job.jd_object_url = request.jd_object_url
    job.cv_submission_deadline = request.cv_submission_deadline
    job.test_start_date = request.test_start_date
    job.test_end_date = request.test_end_date
    job.interview_start_date = request.interview_start_date
    job.interview_end_date = request.interview_end_date
    job.result_announcement_date = request.result_announcement_date
    job.is_active = request.is_active
    job.cv_pass_quota = request.cv_pass_quota
    job.assessment_pass_quota = request.assessment_pass_quota
    job.interview_pass_quota = request.interview_pass_quota
    
    if request.dynamic_test_config:
        job.dynamic_test_config = request.dynamic_test_config.model_dump()

    db.commit()
    db.refresh(job)
    return JobResponse.from_model(job)


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return None


@router.post("/{job_id}/finalize-cv-round")
def finalize_cv_round(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    task_id = enqueue("agent.process_cohort_advancement", {"job_id": str(job_id)})
    return {"message": "Batch transition triggered", "task_id": task_id}

