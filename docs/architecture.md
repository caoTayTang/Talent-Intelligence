# Architecture

## Runtime Components

- `apps/web`: Next.js UI for candidate and HR workflows.
- `apps/api`: FastAPI service for CRUD, upload presigning, and Celery task publishing.
- `apps/worker`: Celery worker that executes scaffolded agent tasks from RabbitMQ.
- `packages/shared`: shared application statuses, labels, and API-facing types.
- `RabbitMQ`: durable task broker with agent-specific queues.
- `PostgreSQL + pgvector`: source of truth and future vector store for RAG.
- `Cloudflare R2`: object storage for CVs, test submissions, job assets, and transcripts.

## Core Flow

```txt
Candidate requests upload URL
API returns R2 presigned URL
Candidate uploads CV directly to R2
API creates Application(status=pending_cv)
API publishes agent.cv_screening task to RabbitMQ
Celery worker runs CV Screener
Celery worker updates Application(status=cv_passed | cv_failed)
Candidate submits test
API publishes agent.assessment task to RabbitMQ
Celery worker updates Application(status=test_scored, totalScore)
HR invites candidate to interview
```

## Queue Design

Initial queues:

```txt
agent.cv_screening
agent.assessment
agent.transcriber
agent.job_assistant
agent.manager
agent.dead_letter
```

For known product events, publish directly to the target task queue. Use `agent.manager` later only when routing becomes dynamic.

## Storage

Store R2 object keys in PostgreSQL, not only public URLs. Public URLs can change; object keys are stable.

## Agent Boundary

Agent tasks should return structured JSON and write an `AgentRun` row for auditability. For the MVP, Celery tasks update PostgreSQL directly. Add a separate result-validation service only if centralized validation becomes necessary.
