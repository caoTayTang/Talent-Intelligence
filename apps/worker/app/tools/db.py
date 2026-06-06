import json
import uuid

import psycopg

from app.config import settings


def load_application_context(application_id: str) -> dict:
    """
    load application + Job context needed by the agent graph
    Keep RabbitMQ payloads small. The Celery task passes application_id,
    and this tool loads the rest from Postgre
    """

    with psycopg.connect(settings.psycopg_database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    a.id,
                    a.job_id,
                    a.cv_object_key,
                    j.description,
                    j.scorecard_json
                FROM applications a 
                JOIN jobs j on j.id = a.job_id
                WHERE a.id = %s
                """,
                (application_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise ValueError(f"Application not found: {application_id}")

    return {
        "application_id": application_id,
        "job_id": str(row[1]),
        "cv_object_key": row[2],
        "jd_text": row[3],
        "scorecard_json": row[4],
    }


def save_agent_run(
    application_id: str, agent_type: str, input_json: dict, output_json: dict
) -> None:
    """
    Store one agent execution record for audit/debugging
    """

    with psycopg.connect(settings.psycopg_database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agent_runs (
                    id,
                    application_id,
                    agent_type, 
                    input_json,
                    output_json,
                    status,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, 'succeeded', NOW(), NOW())
                """,
                (
                    str(uuid.uuid4()),
                    application_id,
                    agent_type,
                    json.dumps(input_json),
                    json.dumps(output_json),
                ),
            )


def update_cv_screening_result(
    application_id: str, cv_score: float, decision: str, output: dict
) -> None:
    """
    Update application after CV screening graph finishes
    """
    status = "cv_passed" if decision == "pass" else "cv_failed"
    with psycopg.connect(settings.psycopg_database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE applications
                SET
                    cv_score = %s,
                    detailed_score_json = %s,
                    status = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    str(cv_score),
                    json.dumps(output),
                    status,
                    str(application_id),
                ),
            )
