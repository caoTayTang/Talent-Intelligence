from app.celery_app import celery_app

# NOTE: can doi ten cua agent + Queue thi doi ten o day
TASK_TO_QUEUE = {
    # "agent.manager": "agent.manager",
    # "agent.job_assistant": "agent.job_assistant",
    # "agent.assessment": "agent.assessment",
    # "agent.transcriber": "agent.transcriber",
    "agent.cv_screening": "agent.cv_screening",
}


def enqueue(task_name: str, payload: dict) -> str:
    queue_name = TASK_TO_QUEUE[task_name]
    async_result = celery_app.send_task(
        task_name,
        args=[payload],
        queue=queue_name,
        routing_key=queue_name,
    )
    return async_result.id
