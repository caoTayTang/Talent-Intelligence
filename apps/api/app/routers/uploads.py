from fastapi import APIRouter, HTTPException

from app.schemas.uploads import PresignUploadRequest, PresignUploadResponse
from app.services.storage import create_presigned_upload_url

router = APIRouter()

@router.post("/presign", response_model=PresignUploadResponse)
def presign_upload(request: PresignUploadRequest) -> PresignUploadResponse:
    """
    Tao 1 cai url ngan han (short-lived) R2 pesigned url
    Frontend:
    - call endpoint nay + file metadata (file name, content type, kind)
    - upload the file directly to R2 using returned URL
    - send the return object_key back to the ... endpoint
    """
    allow_kinds = {"cv", "test-submission", "job-asset", "interview-audio", "transcript"}
    if request.kind not in allow_kinds:
        raise HTTPException(status_code=400, detail="Unsupported upload kind")
    
    return create_presigned_upload_url(
        kind=request.kind,
        file_name=request.file_name,
        content_type=request.content_type,
    )