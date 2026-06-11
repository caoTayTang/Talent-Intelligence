from pydantic import BaseModel
from uuid import UUID
from talent_core.models import Application


class CreateApplicationRequest(BaseModel):
    candidate_id: UUID
    job_id: UUID
    cv_object_key: str


class SubmitTestRequest(BaseModel):
    test_answer: dict | list | None = None
    test_submission_url: list[str] | None = None


class ApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    status: str

    cv_object_key: str | None = None
    dynamic_test_content: dict | list | None = None
    test_submission_url: list[str] | None = None
    test_answer: dict | list | None = None

    cv_score: float | None = None
    total_score: float | None = None
    interview_score: float | None = None
    detailed_score_json: dict | None = None

    @classmethod
    def from_model(cls, application: Application) -> "ApplicationResponse":
        return cls(
            id=application.id,
            candidate_id=application.candidate_id,
            job_id=application.job_id,
            status=application.status.value,
            cv_object_key=application.cv_object_key,
            dynamic_test_content=application.dynamic_test_content,
            test_submission_url=application.test_submission_url,
            test_answer=application.test_answer,
            cv_score=application.cv_score,
            total_score=application.total_score,
            interview_score=application.interview_score,
            detailed_score_json=application.detailed_score_json,
        )

