# Talent Intelligence

Multi-agent ATS scaffold for gated recruiting workflows: CV screening, take-home assessment, interview scheduling, and transcription.

## Stack

- Web: Next.js
- API: FastAPI
- Database: PostgreSQL + pgvector
- Queue: RabbitMQ + Celery
- Storage: Cloudflare R2
- ORM: SQLAlchemy
- Deployment scaffold: Docker + Kubernetes manifests

## Structure

```txt
apps/web       Candidate and HR UI
apps/api       FastAPI service, SQLAlchemy models, R2 adapter, Celery publisher
apps/worker    Celery worker with scaffolded agent tasks
packages/shared Shared types and state machine helpers
docs           Architecture and wireframes
deploy         Docker/Kubernetes deployment scaffold
```

## Local Setup On Ubuntu

Install system tools first:

```bash
sudo apt update
sudo apt install -y python3 nodejs npm docker.io docker-compose-plugin
```


If `uv` is not installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install project dependencies:

```bash
npm install
uv venv
uv pip install --python .venv/bin/python -r apps/api/requirements.txt -r apps/worker/requirements.txt -e packages/backend_shared
cp .env.example .env
```

Start local infrastructure:

```bash
docker compose up -d
```

This starts:

```txt
PostgreSQL: localhost:5432
RabbitMQ AMQP: localhost:5672
RabbitMQ UI: http://localhost:15672
RabbitMQ login: guest / guest
```

Create database tables:

```bash
npm run db:migrate
```

Run app services in separate terminals. The API and worker commands use the local `.venv` environment.

Terminal 1:

```bash
npm run dev:web
```

Terminal 2:

```bash
source .venv/bin/activate
npm run dev:api
```

Terminal 3:

```bash
source .venv/bin/activate
npm run dev:worker
```

URLs:

```txt
Web: http://localhost:3000
API: http://localhost:4000
API docs: http://localhost:4000/docs
RabbitMQ UI: http://localhost:15672
```

## Windows / WSL2 Setup

Recommended path for Windows contributors:

1. Install Docker Desktop.
2. Enable the WSL2 backend in Docker Desktop.
3. Install Ubuntu from Microsoft Store.
4. Clone and run this project inside the Ubuntu WSL2 terminal.
5. Use the Ubuntu setup commands above.

This avoids most native Windows issues with Python workers and shell scripts.

If running Celery on native Windows, use the solo pool:

```bash
npm run dev:windows --workspace @talent-intelligence/worker
```

Or run Celery directly:

```bash
cd apps/worker
celery -A app.celery_app worker --loglevel=info --pool=solo -Q agent.cv_screening,agent.assessment,agent.transcriber,agent.job_assistant,agent.manager
```

For the cleanest experience, prefer WSL2.

## Queue Model

FastAPI publishes named Celery tasks to RabbitMQ:

```txt
agent.cv_screening
agent.assessment
agent.transcriber
agent.job_assistant
agent.manager
```

The worker consumes those queues and updates PostgreSQL directly. The current agent behavior is mocked so product flow can be built before LLM logic is finalized.

## R2 Upload Model

The browser should upload files directly to Cloudflare R2 using presigned URLs:

```txt
Frontend asks API for presigned URL
API returns object key + upload URL
Frontend uploads file directly to R2
API stores the R2 object key in PostgreSQL
Worker reads object keys when agent tasks run
```
