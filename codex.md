# Talent Intelligence Project Notes

This document is a practical handoff and planning guide for agents working on this repository.

## Project Summary

Talent Intelligence is a multi-agent ATS scaffold for gated recruiting workflows:

```txt
candidate applies
-> CV screening
-> test generation
-> test scoring
-> interview scheduling
-> meeting transcript ingestion
-> interview scoring and summary
-> final HR decision support
```

The current codebase implements the foundation:

- Next.js frontend demo console.
- FastAPI CRUD/upload API.
- PostgreSQL + pgvector database.
- SQLAlchemy ORM models.
- Alembic migrations.
- RabbitMQ + Celery task queue.
- Cloudflare R2 presigned uploads.
- LangGraph CV screening workflow.
- Partial dynamic test generation graph.

The system is still a scaffold. CV screening is the most complete workflow. Test scoring, interview orchestration, transcript processing, and final decision aggregation still need implementation.

## Repository Modules

### `apps/web`

Next.js frontend.

Important files:

- `apps/web/app/page.tsx`: main CV screening console. It creates company, candidate, job, application records, uploads/passes a CV object key, queues screening, and polls for results.
- `apps/web/app/dashboard/hr/page.tsx`: static HR dashboard mock.
- `apps/web/app/globals.css`: global styles.

Current status:

- Main page is connected to API routes.
- HR dashboard is mostly static.
- No full applicant lifecycle UI yet.

### `apps/api`

FastAPI backend.

Important files:

- `apps/api/app/main.py`: FastAPI app setup and router registration.
- `apps/api/app/routers/companies.py`: company create/read.
- `apps/api/app/routers/users.py`: local user create/read.
- `apps/api/app/routers/jobs.py`: job create/read.
- `apps/api/app/routers/applications.py`: application create/read/test submission.
- `apps/api/app/routers/uploads.py`: R2 presigned upload URL endpoint.
- `apps/api/app/routers/agent_runs.py`: reads agent audit rows.
- `apps/api/app/queue.py`: task-name to queue mapping.
- `apps/api/app/celery_app.py`: API-side Celery configuration.
- `apps/api/migrations`: Alembic migration environment and revision files.

Current API surface:

```txt
GET  /health
POST /uploads/presign
POST /companies
GET  /companies/{company_id}
POST /users
GET  /users/{user_id}
POST /jobs
GET  /jobs/{job_id}
POST /applications
GET  /applications/{application_id}
POST /applications/{application_id}/submit-test
GET  /agent_runs/{agent_run_id}
```

Current status:

- CRUD routes are minimal but usable.
- `/applications` queues `agent.cv_screening`.
- `/applications/{id}/submit-test` attempts to queue `agent.assessment`, but that task is not currently routed or implemented.

### `apps/worker`

Celery worker and agent orchestration.

Important files:

- `apps/worker/app/tasks.py`: Celery task definitions.
- `apps/worker/app/celery_app.py`: worker-side Celery queues/routes.
- `apps/worker/app/orchestration/cv_screening_graph.py`: implemented LangGraph CV screening workflow.
- `apps/worker/app/orchestration/question_generator_graph.py`: partial dynamic test generation graph.
- `apps/worker/app/orchestration/state.py`: graph state types.
- `apps/worker/app/tools/db.py`: worker DB helpers.
- `apps/worker/app/tools/r2.py`: private R2 object loading.
- `apps/worker/app/tools/documents.py`: document parsing helpers.
- `apps/worker/app/tools/text_cleanup.py`: CV/JD text cleanup.
- `apps/worker/app/tools/profile_extraction.py`: candidate profile extraction.
- `apps/worker/app/tools/rubric.py`: JD rubric extraction/default rubric.
- `apps/worker/app/tools/embeddings.py`: OpenAI-compatible embedding API.
- `apps/worker/app/tools/vector_store.py`: pgvector insert/search helpers.
- `apps/worker/app/tools/evidence.py`: evidence object creation and GitHub/Tavily verification.
- `apps/worker/app/tools/evidence_review.py`: bounded ReAct evidence review.
- `apps/worker/app/tools/rubric_scoring.py`: deterministic rubric scoring.
- `apps/worker/app/tools/llm.py`: OpenAI-compatible chat JSON helper.

Current status:

- `agent.cv_screening` is implemented.
- `agent.test_generation` is present as a graph but its Celery task is commented out.
- `agent.assessment`, `agent.transcriber`, `agent.interview_scoring`, and final decision agents are not yet implemented.

### `packages/backend_shared`

Shared Python package used by both API and worker.

Important files:

- `packages/backend_shared/talent_core/models.py`: canonical SQLAlchemy ORM models.
- `packages/backend_shared/talent_core/db.py`: SQLAlchemy `Base`, `engine`, `SessionLocal`, `get_db`.
- `packages/backend_shared/talent_core/config.py`: database settings loaded from `.env`.

Use this package for all shared DB/domain code. Do not recreate separate API and worker model definitions.

### `packages/shared`

Shared TypeScript package for frontend-facing types and state labels.

Important files:

- `packages/shared/src/application-status.ts`
- `packages/shared/src/types.ts`
- `packages/shared/src/index.ts`

### `deploy`

Deployment scaffold.

Important files:

- `docker-compose.yml`: local PostgreSQL + RabbitMQ.
- `deploy/k8s/base`: Kubernetes examples for API, worker, web, config, secrets, ingress.

## Runtime Infrastructure

Local infrastructure:

```txt
PostgreSQL + pgvector: localhost:5432
RabbitMQ AMQP:       localhost:5672
RabbitMQ UI:         http://localhost:15672
Web:                 http://localhost:3000
API:                 http://localhost:4000
API docs:            http://localhost:4000/docs
```

Primary commands:

```bash
docker compose up -d
npm install
uv venv
uv pip install --python .venv/bin/python -r apps/api/requirements.txt -r apps/worker/requirements.txt -e packages/backend_shared
npm run db:migrate
npm run dev:web
npm run dev:api
npm run dev:worker
```

On native Windows, Celery usually needs the solo pool:

```bash
npm run dev:windows --workspace @talent-intelligence/worker
```

## Environment Variables

The shared database config reads `.env` from the repo root.

Core variables:

```txt
DATABASE_URL=postgresql://talent:talent@localhost:5432/talent_intelligence
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://
```

R2:

```txt
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=talent-intelligence-dev
```

LLM:

```txt
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=
MODEL_NAME=llama-3.3-70b-versatile
```

Embeddings:

```txt
EMBEDDING_BASE_URL=https://api.scaleway.ai/v1
EMBEDDING_API_KEY=
EMBEDDING_MODEL_NAME=qwen3-embedding-8b
EMBEDDING_DIMENSION=4096
```

Public evidence search:

```txt
TAVILY_API_KEY=
```

## Database Design

The canonical ORM schema is in `packages/backend_shared/talent_core/models.py`.

### Enums

`UserRole`

```txt
hr
candidate
```

`ApplicationStatus`

```txt
pending_cv
cv_passed
cv_failed
test_submitted
test_scored
test_failed
interview_scheduled
interview_completed
interview_failed
accepted
```

`AgentRunStatus`

```txt
queued
running
succeeded
failed
```

`SenderRole`

```txt
user
agent
```

`NotificationType`

```txt
test_unlocked
interview_invited
system_alert
```

`InterviewStatus`

```txt
scheduled
ongoing
completed
cancelled
```

`DocumentOwnerType`

```txt
job
application
```

`DocumentChunkSource`

```txt
jd
cv
```

### Tables

`users`

- Candidate and HR accounts.
- Has relationships to applications, interview slots, notifications, chat sessions.

`companies`

- Company profile.
- Has many jobs.

`jobs`

- Job description and test configuration.
- Important fields:
  - `description`
  - `test_content`
  - `test_object_url`
  - `scorecard_json`
  - `jd_object_url`
  - `dynamic_test_config`
  - `test_duration`

`applications`

- Candidate application for a job.
- Unique constraint on `(candidate_id, job_id)`.
- Important fields:
  - `cv_object_key`
  - `dynamic_test_content`
  - `test_submission_url`
  - `test_answer`
  - `interview_audio_url`
  - `interview_transcript`
  - `cv_score`
  - `total_score`
  - `interview_score`
  - `detailed_score_json`
  - `test_deadline`
  - `status`

`agent_runs`

- Audit log for agent execution.
- Stores:
  - `application_id`
  - `agent_type`
  - `input_json`
  - `output_json`
  - `status`
  - `error`

`document_chunks`

- Vector store for RAG/evidence retrieval.
- Important fields:
  - `owner_type`: job/application.
  - `owner_id`: owning job or application UUID.
  - `source`: jd/cv.
  - `section`
  - `chunk_text`
  - `embedding`: `Vector(4096)`.
  - `metadata_json`

`notifications`

- Candidate/HR notification rows.

`chat_sessions` and `chat_messages`

- Candidate/job Q&A chat scaffold.

`interview_slots`

- Interview scheduling and Jitsi room metadata.
- Important fields:
  - `hr_id`
  - `application_id`
  - `start_time`
  - `end_time`
  - `jitsi_room_name`
  - `room_password`
  - `status`

## Alembic Workflow

Alembic is the source of truth for schema changes. Do not use `Base.metadata.create_all()` for real schema updates.

Correct workflow:

```bash
cd apps/api
alembic current
alembic heads
alembic revision --autogenerate -m "describe schema change"
```

Then open the generated migration in:

```txt
apps/api/migrations/versions
```

Review it manually before applying:

```bash
alembic upgrade head
```

From repo root, the intended shortcut is:

```bash
npm run db:migrate
```

Important migration notes:

- Current DB models use `Vector(4096)` for `document_chunks.embedding`.
- Earlier docs mention `Vector(2048)`, but the latest model and migration use 4096.
- The 4096 dimension matches the configured Scaleway `qwen3-embedding-8b` embedding model.
- If the embedding provider changes, update both:
  - `EMBEDDING_DIMENSION`
  - `DocumentChunk.embedding`
  - an Alembic migration to alter the vector column.
- Do not edit old migrations after they are shared or deployed. Add a new migration.
- `apps/api/app/db_migrate.py` is stale and should not be used as the migration path.

## Current Agent Flow

### Implemented CV Screening Flow

Trigger:

```txt
POST /applications
-> create Application(status=pending_cv)
-> enqueue agent.cv_screening
-> Celery worker consumes agent.cv_screening
-> run_cv_screening_graph(application_id)
```

LangGraph flow:

```txt
load_context
-> load_cv_text
-> clean_cv_text
-> extract_cv_profile
-> extract_jd_rubric
-> chunk_documents
-> embed_and_index
-> retrieve_rubric_evidence
-> verify_public_evidence
-> score_rubric
-> react_review_unresolved_evidence
-> persist_result
```

What it does:

1. Loads the application and job from PostgreSQL.
2. Loads the CV object from private Cloudflare R2.
3. Parses/cleans CV text.
4. Extracts a candidate profile.
5. Builds a JD rubric from `scorecard_json`, or uses the default rubric.
6. Chunks CV and rubric/JD text.
7. Calls the embedding provider.
8. Stores CV/JD chunks in `document_chunks`.
9. Retrieves rubric-to-CV evidence with pgvector cosine search.
10. Verifies GitHub/Tavily public evidence.
11. Scores criteria deterministically.
12. Runs a bounded ReAct-style evidence review.
13. Writes an `agent_runs` audit row.
14. Updates `applications.cv_score`, `applications.detailed_score_json`, and application status.

This is not basic RAG. It is a LangGraph evidence pipeline that includes RAG, deterministic rubric scoring, public evidence verification, ReAct-style review, and audit persistence.

### Partial Test Generation Flow

There is a graph in `apps/worker/app/orchestration/question_generator_graph.py`.

Intended flow:

```txt
load_context
-> generate_questions
-> validate_questions
-> persist_test
```

What it should do:

1. Load JD, CV profile, and dynamic test config.
2. Generate a competency test with an LLM.
3. Validate/refine the generated test with another LLM pass.
4. Store `Application.dynamic_test_content`.
5. Set `Application.status = cv_passed`.
6. Set `Application.test_deadline`.
7. Create a `test_unlocked` notification.

Current caveat:

- The Celery task for test generation is commented out.
- `cv_screening` calls `task_test_generation` when CV decision is pass, but the callable task is commented out. This needs to be fixed before relying on CV pass -> test generation.

### Missing Scoring/Test Assessment Flow

The API currently accepts test submissions:

```txt
POST /applications/{application_id}/submit-test
```

It stores:

- `test_answer`
- `test_submission_url`
- `status = test_submitted`

Then it attempts to enqueue:

```txt
agent.assessment
```

Current caveat:

- `agent.assessment` is not configured in `apps/api/app/queue.py`.
- `agent.assessment` is not configured in Celery routes.
- No worker task currently implements assessment scoring.

## Target End-to-End Agent Workflow

The desired workflow should become:

```txt
1. CV Screening Agent
   Input: application_id
   Reads: Application, Job, CV object, scorecard
   Writes: AgentRun, cv_score, detailed_score_json.cv_screening, status
   Next: if pass, trigger Test Generation Agent

2. Test Generation Agent
   Input: application_id
   Reads: JD, CV profile, dynamic_test_config or fixed test_content
   Writes: dynamic_test_content, test_deadline, notification
   Next: wait for candidate submission

3. Test Scoring Agent
   Trigger: POST /applications/{id}/submit-test
   Input: application_id
   Reads: dynamic_test_content, test_answer, test_submission_url, CV/JD context
   Writes: total_score, detailed_score_json.assessment, status
   Next: if pass, unlock interview scheduling or notify HR

4. Interview Scheduling Agent or API Flow
   Trigger: HR action or automated threshold
   Reads: application score summary, HR availability
   Writes: interview_slots, status=interview_scheduled, notification
   Next: wait for interview completion/transcript

5. Transcript Ingestion Agent
   Trigger: uploaded transcript/audio
   Reads: interview_audio_url or transcript object
   Writes: interview_transcript, status=interview_completed
   Next: trigger Interview Scoring Agent

6. Interview Scoring and Summary Agent
   Input: application_id
   Reads: JD rubric, CV profile, test results, transcript
   Writes: interview_score, detailed_score_json.interview, summary, risk flags
   Next: trigger Final Decision Agent

7. Final Decision Agent
   Input: application_id
   Reads: CV score, test score, interview score, all agent runs
   Writes: final recommendation, total_score, detailed_score_json.final_decision
   Next: HR dashboard review and manual decision
```

## Recommended `detailed_score_json` Shape

Right now `detailed_score_json` stores the CV screening output. For multiple phases, use a namespaced object:

```json
{
  "cv_screening": {
    "score": 82.5,
    "decision": "pass",
    "decision_band": "pass",
    "criteria": [],
    "evidence": [],
    "risk_flags": [],
    "summary": ""
  },
  "assessment": {
    "score": 88,
    "decision": "pass",
    "question_scores": [],
    "rubric_feedback": [],
    "summary": ""
  },
  "interview": {
    "score": 79,
    "decision": "review",
    "competency_scores": [],
    "transcript_summary": "",
    "risk_flags": [],
    "follow_up_questions": []
  },
  "final_decision": {
    "total_score": 83,
    "recommendation": "advance",
    "reasoning": [],
    "hr_notes": []
  }
}
```

This avoids overwriting CV details when later phases run.

## Known Issues And Caveats

1. `apps/api/app/db_migrate.py` is stale and should not be used.
2. `docs/alembic.md` mentions `Vector(2048)`, but code/migrations currently use `Vector(4096)`.
3. `npm run db:migrate` should be verified locally because the `PYTHONPATH` may need to point at `packages/backend_shared`, not `packages/backend_shared/talent_core`.
4. Only `agent.cv_screening` is fully configured.
5. `agent.assessment` is called by API but is not currently routed or implemented.
6. `task_test_generation` is commented out but referenced by `cv_screening`.
7. `jobs.py` accepts `dynamic_test_config` and `test_duration` in the schema, but `create_job()` currently does not pass them into the `Job` model.
8. There is no frontend flow yet for test submission, interview scheduling, transcript upload, or final HR decision.
9. There are no automated tests visible in the current scaffold.

## Implementation Plan

### Phase 1: Stabilize Current CV Screening

Success criteria:

- Creating an application reliably queues CV screening.
- Passing CV screening does not crash.
- Agent output is stored without destroying previous phase data.

Tasks:

1. Fix `cv_screening` pass path.
   - Either restore `agent.test_generation`, or temporarily guard the call.
   - Verify by running a CV screening task with a passing score.

2. Fix job creation fields.
   - Persist `dynamic_test_config`.
   - Persist `test_duration`.
   - Verify by creating a job and reading it back.

3. Normalize `detailed_score_json`.
   - Store CV output under `detailed_score_json["cv_screening"]`.
   - Preserve existing keys during updates.
   - Verify that later updates do not erase CV evidence.

4. Add basic tests for API create/read flows and worker DB update helpers.

### Phase 2: Integrate Test Generation

Success criteria:

- A CV pass triggers test generation.
- Generated test is saved to the application.
- Candidate receives a test deadline and notification.

Tasks:

1. Restore/register `agent.test_generation`.
2. Add queue route in:
   - `apps/api/app/queue.py`
   - `apps/api/app/celery_app.py`
   - `apps/worker/app/celery_app.py`
3. Fix import boundaries in `question_generator_graph.py`.
   - Avoid importing API schemas from worker if it creates package/runtime issues.
   - Prefer shared schemas or worker-local validation if needed.
4. Handle fixed HR-provided `job.test_content`.
   - If fixed test exists, copy it to `Application.dynamic_test_content`.
   - If dynamic config exists, generate test.
   - If neither exists, set CV passed and wait for HR.
5. Add frontend display for generated test content.

### Phase 3: Add Test Scoring Agent

Success criteria:

- Candidate test submission triggers scoring.
- `total_score` and assessment details are persisted.
- Application moves to `test_scored` or `test_failed`.

Tasks:

1. Implement `agent.assessment`.
2. Add queue routes for `agent.assessment`.
3. Create `assessment_scoring_graph.py`.
4. Score by question type:
   - multiple choice: deterministic exact answer scoring.
   - essay: LLM rubric scoring against `expected_answer`.
   - file upload: parse files if supported, otherwise include metadata and require manual review.
5. Store results under `detailed_score_json["assessment"]`.
6. Add status logic:
   - pass threshold -> `test_scored`.
   - fail threshold -> `test_failed`.
7. Add frontend test submission UI.

### Phase 4: Interview Scheduling

Success criteria:

- HR can schedule interview slots.
- Candidate can see invitation details.
- Application status moves to `interview_scheduled`.

Tasks:

1. Add API endpoints for interview slots:
   - create slot
   - assign application
   - list slots by HR/candidate/application
   - update/cancel slot
2. Generate stable Jitsi room name and optional room password.
3. Create notification type/use existing `interview_invited`.
4. Add HR dashboard action to invite/schedule.
5. Add candidate interview view.

### Phase 5: Transcript Ingestion

Success criteria:

- Interview transcript/audio can be uploaded.
- Transcript text is stored on the application.
- Completion triggers interview scoring.

Tasks:

1. Add transcript/audio upload flow using `/uploads/presign`.
2. Add API endpoint:
   - `POST /applications/{id}/interview-transcript`
3. If audio is uploaded, implement `agent.transcriber`.
4. If transcript JSON/text is uploaded, parse and normalize directly.
5. Store normalized transcript in `Application.interview_transcript`.
6. Trigger `agent.interview_scoring`.

### Phase 6: Interview Scoring And Summary Agent

Success criteria:

- Transcript is scored against the JD and previous evidence.
- Interview summary is visible to HR.
- `interview_score` is persisted.

Tasks:

1. Implement `interview_scoring_graph.py`.
2. Inputs:
   - JD rubric.
   - CV screening evidence.
   - test scoring evidence.
   - transcript.
3. Outputs:
   - competency scores.
   - behavioral summary.
   - technical summary.
   - risk flags.
   - follow-up questions.
   - recommendation.
4. Store under `detailed_score_json["interview"]`.
5. Set status to `interview_completed` or `interview_failed`.

### Phase 7: Final Decision Aggregation

Success criteria:

- HR has one final recommendation view.
- Scores are weighted and explainable.
- HR remains the final decision maker.

Tasks:

1. Implement final aggregation helper or `agent.final_decision`.
2. Combine:
   - CV score.
   - test score.
   - interview score.
   - risk flags.
   - missing evidence.
3. Store:
   - `Application.total_score`.
   - `detailed_score_json["final_decision"]`.
4. Add HR dashboard ranking and detail views.
5. Add manual accept/reject endpoint.

## Suggested Immediate Next Steps

Start with the smallest path that removes current blockers:

```txt
1. Fix job creation to save dynamic_test_config/test_duration.
2. Restore or guard test generation after CV pass.
3. Add queue routing for agent.test_generation.
4. Add namespaced detailed_score_json updates.
5. Implement agent.assessment and route submit-test to it.
```

After those five items, the core product loop becomes:

```txt
create application
-> screen CV
-> generate test
-> submit test
-> score test
```

That is the right foundation before investing in interview scheduling and transcript scoring.

