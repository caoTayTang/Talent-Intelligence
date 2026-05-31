from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Application, ApplicationStatus
from app.queue import enqueue
from app.schemas import CreateApplicationRequest, PresignUploadRequest, SubmitTestRequest
from app.storage import create_presigned_upload_url

app = FastAPI(title="Talent Intelligence API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "talent-intelligence-api"}


@app.post("/uploads/presign")
def presign_upload(request: PresignUploadRequest) -> dict:
    allowed_kinds = {"cv", "test-submission", "job-asset", "transcript"}
    if request.kind not in allowed_kinds:
        raise HTTPException(status_code=400, detail="Unsupported upload kind")

    return create_presigned_upload_url(
        kind=request.kind,
        file_name=request.file_name,
        content_type=request.content_type,
    )


@app.post("/applications", status_code=201)
def create_application(request: CreateApplicationRequest, db: Session = Depends(get_db)) -> dict:
    application = Application(
        candidate_id=request.candidate_id,
        job_id=request.job_id,
        cv_object_key=request.cv_object_key,
        status=ApplicationStatus.pending_cv,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    enqueue("cv-screening", {"application_id": str(application.id)})

    return {"id": str(application.id), "status": application.status.value}


@app.post("/applications/{application_id}/submit-test")
def submit_test(application_id: UUID, request: SubmitTestRequest, db: Session = Depends(get_db)) -> dict:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    application.test_answer = request.test_answer
    application.test_object_key = request.test_object_key
    application.status = ApplicationStatus.test_submitted
    db.commit()

    enqueue("assessment", {"application_id": str(application.id)})

    return {"id": str(application.id), "status": application.status.value}


@app.get("/applications/{application_id}")
def get_application(application_id: UUID, db: Session = Depends(get_db)) -> dict:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "id": str(application.id),
        "candidate_id": str(application.candidate_id),
        "job_id": str(application.job_id),
        "status": application.status.value,
        "cv_score": application.cv_score,
        "total_score": application.total_score,
        "cv_object_key": application.cv_object_key,
        "test_object_key": application.test_object_key,
    }
