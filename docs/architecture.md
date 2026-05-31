# Architecture

## Runtime Components

- `apps/web`: Next.js UI for candidate and HR workflows.
- `apps/api`: FastAPI service for jobs, applications, uploads, and scheduling.
- `apps/worker`: Python Redis-list worker that executes scaffolded agent jobs.
- `packages/shared`: shared application statuses, labels, and API-facing types.

## Core Flow

```txt
Candidate uploads CV to R2
API creates Application(status=pending_cv)
API pushes a cv-screening job to Redis
Worker runs CV Screener
Worker updates Application(status=cv_passed | cv_failed)
Candidate submits test
API pushes an assessment job to Redis
Worker updates Application(status=test_scored, totalScore)
HR invites candidate to interview
```

## Storage

Store R2 object keys in Postgres. Generate presigned upload URLs from the API and let the browser upload directly to R2.

## Agent Boundary

Agent workers should always return structured JSON and write an `AgentRun` record for auditability.
