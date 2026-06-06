from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.models import Job


class CreateJobRequest(BaseModel):
    company_id: UUID
    title: str
    description: str
    test_content: dict | list | None = None
    test_object_url: str | None = None
    scorecard_json: dict | None = None
    jd_object_url: str | None = None
    is_active: bool = True


class JobResponse(BaseModel):
    id: UUID
    company_id: UUID
    title: str
    description: str
    test_content: dict | list | None = None
    test_object_url: str | None = None
    scorecard_json: dict | None = None
    jd_object_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, job: Job) -> "JobResponse":
        return cls(
            id=job.id,
            company_id=job.company_id,
            title=job.title,
            description=job.description,
            test_content=job.test_content,
            test_object_url=job.test_object_url,
            scorecard_json=job.scorecard_json,
            jd_object_url=job.jd_object_url,
            is_active=job.is_active,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )