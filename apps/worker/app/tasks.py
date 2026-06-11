from app.celery_app import celery_app
from app.orchestration.cv_screening_graph import run_cv_screening_graph


@celery_app.task(
    name="agent.cv_screening",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cv_screening(self, payload: dict) -> dict:
    application_id = payload["application_id"]
    return run_cv_screening_graph(application_id)
