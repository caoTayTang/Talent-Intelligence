from uuid import UUID

from pydantic import BaseModel


class CreateApplicationRequest(BaseModel):
    candidate_id: UUID
    job_id: UUID
    cv_object_key: str


class SubmitTestRequest(BaseModel):
    test_answer: str | None = None
    test_object_key: str | None = None


class PresignUploadRequest(BaseModel):
    kind: str
    file_name: str
    content_type: str


class PresignUploadResponse(BaseModel):
    object_key: str
    upload_url: str
    expires_in_seconds: int
