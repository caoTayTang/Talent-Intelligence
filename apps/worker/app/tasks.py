from datetime import timezone, timedelta, datetime

from app.celery_app import celery_app
from app.orchestration.cv_screening_graph import run_cv_screening_graph
# from app.orchestration.question_generator_graph import run_generator_graph

from talent_core.models import *
from talent_core.db import SessionLocal

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
    
    if result.get("decision") == "pass":
        task_test_generation.apply_async(kwargs={"payload": {"application_id": application_id}})

    return {"status": "completed", "decision": result.get("decision")}

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
#         with SessionLocal() as db:
#             app = db.query(Application).filter(Application.id == uuid.UUID(application_id)).first()
            
#             if app and app.job:
#                 job = app.job
                
#                 # HR cho đề
#                 if job.test_content:
#                     # Copy đề cứng của HR sang cho ứng viên này
#                     app.dynamic_test_content = job.test_content
                    
#                     app.status = ApplicationStatus.cv_passed
#                     app.test_deadline = datetime.now(timezone.utc) + timedelta(days=job.test_duration)
                    
#                     # Noti
#                     new_noti = Notification(
#                         user_id=app.candidate_id,
#                         type=NotificationType.test_unlocked,
#                         title="Test round unlocked",
#                         message=f"Congrats! {job.title} test has been unlocked. You have {job.test_duration} days to complete it.",
#                         is_read=False
#                     )
#                     db.add(new_noti)
#                     db.commit()
                    
#                 elif job.dynamic_test_config:
#                     task_test_generation.apply_async(kwargs={"payload": {"application_id": application_id}})
#                 else:
#                     # Chỉ đổi trạng thái Pass CV, không giao đề. HR phải tự xử lý bằng tay sau.
#                     app.status = ApplicationStatus.cv_passed
#                     db.commit()

#     return {"status": "completed", "decision": result.get("decision")}

# # Task của Gen Test
# @celery_app.task(name="agent.test_generation", bind=True, max_retries=3)
# def task_test_generation(self, payload: dict):
#     application_id = payload.get("application_id")
#     run_generator_graph(application_id)
#     return {"status": "completed", "application_id": application_id}