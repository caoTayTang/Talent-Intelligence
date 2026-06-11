FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.9.6 /uv /usr/local/bin/uv
COPY apps/worker/requirements.txt ./requirements.txt
COPY packages/backend_shared ./packages/backend_shared
RUN uv pip install --system --no-cache -r requirements.txt -e ./packages/backend_shared

COPY apps/worker/app ./app

CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "-Q", "agent.cv_screening,agent.assessment,agent.transcriber,agent.job_assistant,agent.manager"]
