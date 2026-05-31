import json
import time

import psycopg
from redis import Redis

from app.config import settings


redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def update_cv_screening(application_id: str) -> None:
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
            cur.execute(
                """
                INSERT INTO agent_runs (application_id, agent_type, input_json, output_json, status, created_at, updated_at)
                VALUES (%s, 'cv_screener', %s, %s, 'succeeded', NOW(), NOW())
                """,
                (application_id, json.dumps({"application_id": application_id}), json.dumps(output)),
            )


def update_assessment(application_id: str) -> None:
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
            cur.execute(
                """
                INSERT INTO agent_runs (application_id, agent_type, input_json, output_json, status, created_at, updated_at)
                VALUES (%s, 'assessor', %s, %s, 'succeeded', NOW(), NOW())
                """,
                (application_id, json.dumps({"application_id": application_id}), json.dumps(output)),
            )


def handle_job(queue_name: str, payload: str) -> None:
    job = json.loads(payload)
    application_id = job["application_id"]

    if queue_name == "cv-screening":
        update_cv_screening(application_id)
        return

    if queue_name == "assessment":
        update_assessment(application_id)
        return

    raise ValueError(f"Unknown queue: {queue_name}")


def main() -> None:
    print("Talent Intelligence Python worker is listening.")
    while True:
        item = redis_client.blpop(["cv-screening", "assessment"], timeout=5)
        if item is None:
            time.sleep(1)
            continue

        queue_name, payload = item
        handle_job(queue_name, payload)


if __name__ == "__main__":
    main()
