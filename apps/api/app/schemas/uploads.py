from pydantic import BaseModel, Field

class PresignUploadRequest(BaseModel):
    kind: str = Field(description="Upload category: cv, test-submission, job-asset, interview-audio")
    file_name: str
    content_type: str


class PresignUploadResponse(BaseModel):
    object_key: str
    upload_url: str
    expires_in_seconds: int
