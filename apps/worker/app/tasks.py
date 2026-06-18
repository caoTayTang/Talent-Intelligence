from datetime import timedelta, datetime, timezone

from app.celery_app import celery_app
from app.orchestration.cv_screening_graph import run_cv_screening_graph
from app.orchestration.question_generator_graph import run_generator_graph

from talent_core.models import *
from talent_core.db import SessionLocal

# @celery_app.task(
#     name="agent.cv_screening",
#     bind=True,
#     autoretry_for=(Exception,),
#     retry_backoff=True,
#     retry_kwargs={"max_retries": 3},
# )
# def cv_screening(self, payload: dict) -> dict:
#     application_id = payload["application_id"]
#     result = run_cv_screening_graph(application_id)
    
#     if result.get("decision") == "pass":
#         task_test_generation.apply_async(kwargs={"payload": {"application_id": application_id}})

#     return {"status": "completed", "decision": result.get("decision")}

@celery_app.task(
    name="agent.cv_screening",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cv_screening(self, payload: dict) -> dict:
    application_id = payload["application_id"]
    
    result = run_cv_screening_graph(application_id)
    
    return {"status": "completed", "decision": result.get("decision")}

# Task của Gen Test
@celery_app.task(name="agent.test_generation", bind=True, max_retries=3)
def task_test_generation(self, payload: dict):
    application_id = payload.get("application_id")
    print(payload)
    run_generator_graph(application_id)
    return {"status": "completed", "application_id": application_id}

@celery_app.task(name="agent.process_cohort_advancement", bind=True)
def process_cohort_advancement(self, payload: dict):
    job_id = payload["job_id"]
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job:
            return {"error": "Job not found"}
            
        # 1. Fetch cv_screened apps
        apps = db.query(Application).filter(
            Application.job_id == job_id,
            Application.status == ApplicationStatus.cv_screened
        ).order_by(Application.cv_score.desc()).all()
        
        # 2. Quota
        quota = job.cv_pass_quota if job.cv_pass_quota is not None else len(apps)
        passed_apps = apps[:quota]
        failed_apps = apps[quota:]
        
        # 3. Advance passed
        for app in passed_apps:
            if job.test_content:
                app.dynamic_test_content = job.test_content
                app.status = ApplicationStatus.cv_passed
                app.test_deadline = job.test_end_date
                
                # Notification
                deadline_str = job.test_end_date.strftime("%Y-%m-%d %H:%M") if job.test_end_date else "the specified deadline"
                new_noti = Notification(
                    user_id=app.candidate_id,
                    type=NotificationType.test_unlocked,
                    title="Test round unlocked",
                    message=f"Congrats! {job.title} test has been unlocked. Please complete it by {deadline_str}.",
                    is_read=False
                )
                db.add(new_noti)
            elif job.dynamic_test_config:
                # task_test_generation will update status to cv_passed in update_dynamic_test_content
                task_test_generation.apply_async(kwargs={"payload": {"application_id": str(app.id)}})
            else:
                app.status = ApplicationStatus.cv_passed
                
        # 4. Fail remaining
        for app in failed_apps:
            app.status = ApplicationStatus.cv_failed
            
        db.commit()
    return {"status": "completed", "passed": len(passed_apps), "failed": len(failed_apps)}

