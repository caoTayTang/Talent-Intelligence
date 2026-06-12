from datetime import timedelta
from uuid import UUID

from talent_core.models import *
from sqlalchemy.orm import Session

from talent_core.db import SessionLocal
from talent_core.models import AgentRun, AgentRunStatus, Application, ApplicationStatus


def load_application_context(application_id: str) -> dict:
    """
    Load application and job context needed by the CV screening graph.
    """
    db: Session = SessionLocal()
    try:
        application = db.get(Application, UUID(application_id))
        if application is None:
            raise ValueError(f"Application not found: {application_id}")

        return {
            "application_id": str(application.id),
            "job_id": str(application.job_id),
            "cv_object_key": application.cv_object_key,
            "jd_text": application.job.description,
            "scorecard_json": application.job.scorecard_json,
            "dynamic_test_config": application.job.dynamic_test_config,
        }
    finally:
        db.close()


def save_agent_run(
    application_id: str,
    agent_type: str,
    input_json: dict,
    output_json: dict,
    status: AgentRunStatus = AgentRunStatus.succeeded,
    error: str | None = None,
) -> None:
    """
    Store one agent execution record for audit/debugging.
    """
    db: Session = SessionLocal()
    try:
        db.add(
            AgentRun(
                application_id=UUID(application_id),
                agent_type=agent_type,
                input_json=input_json,
                output_json=output_json,
                status=status,
                error=error,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_cv_screening_result(
    application_id: str, cv_score: float, decision: str, output: dict
) -> None:
    """
    Update application after CV screening graph finishes.
    """
    db: Session = SessionLocal()
    try:
        application = db.get(Application, UUID(application_id))
        if application is None:
            raise ValueError(f"Application not found: {application_id}")

        application.cv_score = cv_score
        application.detailed_score_json = output
        application.status = (
            ApplicationStatus.cv_passed
            if decision == "pass"
            else ApplicationStatus.cv_failed
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def update_dynamic_test_content(application_id: str, test_content: dict) -> None:
    "Update dynamic test content for the application after question generator graph finishes and open Test round for candidates"
    with SessionLocal() as db:
        app = db.query(Application).filter(Application.id == UUID(application_id)).first()
        if not app:
            raise ValueError(f"Application {application_id} not found")

        app.dynamic_test_content = test_content
        
        app.status = ApplicationStatus.cv_passed 

        duration_days = app.job.test_duration if app.job.test_duration else 3
        app.test_deadline = datetime.now(datetime.timezone.utc) + timedelta(days=duration_days)
        
        new_noti = Notification(
            user_id=app.candidate_id,
            type=NotificationType.test_unlocked,
            title="Test round unlocked",
            message=f"Congrats! {app.job.title} test has been unlocked. You have {duration_days} days to complete it.",
            is_read=False
        )
        db.add(new_noti)
        
        db.commit()