import json

import psycopg

from app.celery_app import celery_app
from app.config import settings


def insert_agent_run(cur, application_id: str, agent_type: str, payload: dict, output: dict) -> None:
    cur.execute(
        """
        INSERT INTO agent_runs (application_id, agent_type, input_json, output_json, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, 'succeeded', NOW(), NOW())
        """,
        (application_id, agent_type, json.dumps(payload), json.dumps(output)),
    )


@celery_app.task(name="agent.cv_screening", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def cv_screening(self, payload: dict) -> dict:
    application_id = payload["application_id"]
    cv_score = 86
    status = "cv_passed" if cv_score >= 75 else "cv_failed"
    output = {
        "cv_score": cv_score,
        "recommendation": "pass" if cv_score >= 75 else "fail",
        "reason": "Mocked score for scaffold flow.",
    }

    with psycopg.connect(settings.psycopg_database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE applications
                SET cv_score = %s, status = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (cv_score, status, application_id),
            )
            insert_agent_run(cur, application_id, "cv_screener", payload, output)

    return output


@celery_app.task(name="agent.assessment", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def assessment(self, payload: dict) -> dict:
    application_id = payload["application_id"]
    total_score = 88
    output = {
        "total_score": total_score,
        "criteria": [
            {"label": "Technical correctness", "score": 34, "max": 40},
            {"label": "Reasoning clarity", "score": 28, "max": 30},
            {"label": "Production judgment", "score": 26, "max": 30},
        ],
        "reason": "Mocked assessment for scaffold flow.",
    }

    with psycopg.connect(settings.psycopg_database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE applications
                SET total_score = %s, status = 'test_scored', updated_at = NOW()
                WHERE id = %s
                """,
                (total_score, application_id),
            )
            insert_agent_run(cur, application_id, "assessor", payload, output)

    return output


@celery_app.task(name="agent.transcriber", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def transcriber(self, payload: dict) -> dict:
    return {
        "transcript": "Mocked transcript placeholder.",
        "source": payload,
    }


@celery_app.task(name="agent.manager", bind=True)
def manager(self, payload: dict) -> dict:
    return {
        "routed": False,
        "reason": "Manager routing is reserved for dynamic orchestration later.",
        "payload": payload,
    }


@celery_app.task(name="agent.job_assistant", bind=True)
def job_assistant(self, payload: dict) -> dict:
    return {
        "answer": "Mocked Job Assistant response placeholder.",
        "payload": payload,
    }
