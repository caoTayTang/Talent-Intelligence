from celery import Celery
from kombu import Exchange, Queue

from app.config import settings

agent_exchange = Exchange("agents", type="direct", durable=True)
dead_letter_exchange = Exchange("agents.dlx", type="direct", durable=True)


def agent_queue(name: str) -> Queue:
    return Queue(
        name,
        exchange=agent_exchange,
        routing_key=name,
        durable=True,
        queue_arguments={
            "x-dead-letter-exchange": "agents.dlx",
            "x-dead-letter-routing-key": "agent.dead_letter",
        },
    )


celery_app = Celery(
    "talent_intelligence_worker",
    broker=settings.rabbitmq_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],
)

# NOTE: Sau nay co them agent vo thi add vo cho nay nha!!
celery_app.conf.update(
    # FUTURE QUEUEUS
    # task_default_exchange="agents",
    # task_default_exchange_type="direct",
    # task_default_routing_key="agent.manager", # khi cai task no khong dinh cai task nao thi di vo manager?!
    task_queues=(
        agent_queue("agent.cv_screening"),
        # agent_queue("agent.abcxyz"),
        Queue(
            "agent.dead_letter",
            exchange=dead_letter_exchange,
            routing_key="agent.dead_letter",
            durable=True,
        ),
    ),
    task_routes={
        "agent.cv_screening": {
            "queue": "agent.cv_screening",
            "routing_key": "agent.cv_screening",
        },
    },
    # FUTURE ROUTES TOO...
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
