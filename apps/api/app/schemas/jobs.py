from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

from talent_core.models import Job

class QuestionDistribution(BaseModel):
    count: int = Field(default=0, ge=0, description="number of questions of this type")
    total_category_points: int = Field(default=0, ge=0, description="total points allocated for this type of questions. The sum of total_category_points across all question types should equal total_points in DynamicTestConfig")

class TestDistributionConfig(BaseModel):
    multiple_choice: Optional[QuestionDistribution] = None
    essay: Optional[QuestionDistribution] = None

class DynamicTestConfig(BaseModel):
    total_points: int = Field(default=100, description="total points for the entire test. This should equal the sum of total_category_points in TestDistributionConfig")
    distribution: TestDistributionConfig = Field(description="configuration for how questions should be distributed across different types")

class CreateJobRequest(BaseModel):
    company_id: UUID
    title: str
    description: str
    test_content: dict | list | None = None
    test_object_url: str | None = None
    scorecard_json: dict | None = None
    jd_object_url: str | None = None
    is_active: bool = True

    dynamic_test_config: DynamicTestConfig | None = None
    test_duration: int = Field(default=3, description="Số ngày ứng viên có để làm bài test sau khi Pass CV")


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

    dynamic_test_config: Optional[DynamicTestConfig] = None
    test_duration: int 

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
            dynamic_test_config=job.dynamic_test_config,
            test_duration=job.test_duration,
        )

