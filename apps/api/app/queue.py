import json

from redis import Redis

from app.config import settings


redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue(queue_name: str, payload: dict) -> None:
    redis_client.rpush(queue_name, json.dumps(payload, default=str))
