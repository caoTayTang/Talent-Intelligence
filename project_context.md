# Project Context

Generated for handoff to another AI assistant after rescanning the current workspace.

## Directory Structure (Working Tree)

Excluded: `.git`, `.env*`, `.venv`, `venv`, `node_modules`, `__pycache__`, `dist`, `build`, and generated cache directories.

```text
Talent-Intelligence/
├── AGENTS.md
├── README.md
├── docker-compose.yml
├── package-lock.json
├── package.json
├── project_context.md
├── tsconfig.base.json
├── apps/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── alembic.ini
│   │   ├── package.json
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── config.py
│   │   │   ├── db_migrate.py
│   │   │   ├── main.py
│   │   │   ├── queue.py
│   │   │   ├── routers/
│   │   │   │   ├── agent_runs.py
│   │   │   │   ├── applications.py
│   │   │   │   ├── companies.py
│   │   │   │   ├── health.py
│   │   │   │   ├── jobs.py
│   │   │   │   ├── uploads.py
│   │   │   │   └── users.py
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── applications.py
│   │   │   │   ├── companies.py
│   │   │   │   ├── jobs.py
│   │   │   │   ├── uploads.py
│   │   │   │   └── users.py
│   │   │   └── services/
│   │   │       ├── __init__.py
│   │   │       └── storage.py
│   │   ├── migrations/
│   │   │   ├── README
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/
│   │   │       ├── 1a7642072efd_initial_schema.py
│   │   │       ├── 38289d6e6f86_add_document_chunks.py
│   │   │       ├── 3e4e86fbbe64_change_document_chunk_embedding_.py
│   │   │       └── 6be302d65b1a_create_missing_app_tables.py
│   │   └── scripts/
│   │       └── publish_application.py
│   ├── web/
│   │   ├── Dockerfile
│   │   ├── next-env.d.ts
│   │   ├── next.config.ts
│   │   ├── package.json
│   │   ├── postcss.config.js
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   └── app/
│   │       ├── globals.css
│   │       ├── layout.tsx
│   │       ├── page.tsx
│   │       └── dashboard/
│   │           └── hr/
│   │               └── page.tsx
│   └── worker/
│       ├── Dockerfile
│       ├── package.json
│       ├── requirements.txt
│       └── app/
│           ├── __init__.py
│           ├── celery_app.py
│           ├── config.py
│           ├── main.py
│           ├── tasks.py
│           ├── orchestration/
│           │   ├── __init__.py
│           │   ├── cv_screening_graph.py
│           │   └── state.py
│           └── tools/
│               ├── __init__.py
│               ├── chunking.py
│               ├── db.py
│               ├── documents.py
│               ├── embeddings.py
│               ├── evidence.py
│               ├── evidence_review.py
│               ├── llm.py
│               ├── profile_extraction.py
│               ├── r2.py
│               ├── rubric.py
│               ├── rubric_scoring.py
│               ├── scoring.py
│               ├── text_cleanup.py
│               ├── vector_store.py
│               └── web_search.py
├── deploy/
│   ├── README.md
│   └── k8s/
│       └── base/
│           ├── api.yaml
│           ├── configmap.yaml
│           ├── ingress.yaml
│           ├── namespace.yaml
│           ├── secret.example.yaml
│           ├── web.yaml
│           └── worker.yaml
├── docs/
│   ├── alembic.md
│   ├── architecture.md
│   └── wireframes.md
└── packages/
    ├── backend_shared/
    │   ├── pyproject.toml
    │   └── talent_core/
    │       ├── __init__.py
    │       ├── config.py
    │       ├── db.py
    │       └── models.py
    └── shared/
        ├── package.json
        ├── tsconfig.json
        └── src/
            ├── application-status.ts
            ├── index.ts
            └── types.ts
```

## Core Dependencies

### Python API (`apps/api/requirements.txt`)

- `fastapi==0.115.6`
- `uvicorn[standard]==0.34.0`
- `sqlalchemy==2.0.36`
- `psycopg[binary]==3.2.3`
- `celery==5.4.0`
- `boto3==1.35.90`
- `pydantic-settings==2.7.1`
- `alembic` (currently unpinned)
- `pgvector==0.3.6`

### Python Worker (`apps/worker/requirements.txt`)

- `celery==5.4.0`
- `psycopg[binary]==3.2.3`
- `pydantic-settings==2.7.1`
- `langgraph` (currently unpinned)
- `boto3` (currently unpinned)
- `pdfplumber` (currently unpinned)
- `python-docx` (currently unpinned)
- `httpx==0.28.1`

### Shared Backend Package (`packages/backend_shared/pyproject.toml`)

- Package name: `talent-core`
- Python: `>=3.12`
- `sqlalchemy==2.0.36`
- `psycopg[binary]==3.2.3`
- `pydantic-settings==2.7.1`
- `pgvector==0.3.6`

### JavaScript / TypeScript Workspace

- Root dev dependency: `typescript^5.5.4`
- Web app: `next^15.0.0`, `react^19.0.0`, `react-dom^19.0.0`, `lucide-react^0.468.0`, `tailwindcss^3.4.10`, `postcss^8.4.41`, `autoprefixer^10.4.20`
- Shared frontend package: `@talent-intelligence/shared`

## Database Work Completed

### Current Shape

- SQLAlchemy database/domain code has moved out of `apps/api/app` into `packages/backend_shared/talent_core`.
- `talent_core.db` now owns `Base`, `engine`, `SessionLocal`, and `get_db()`.
- API routers import `get_db` and models from `talent_core`.
- Worker tools also use `talent_core.db.SessionLocal` and `talent_core.models`.
- PostgreSQL local infrastructure still uses `pgvector/pgvector:pg16` in `docker-compose.yml`.

### Current Tables

The current ORM schema is in `packages/backend_shared/talent_core/models.py` and defines:

- `users`
- `notifications`
- `companies`
- `jobs`
- `chat_sessions`
- `chat_messages`
- `applications`
- `interview_slots`
- `agent_runs`
- `document_chunks`

`document_chunks` is the new pgvector/RAG table. It stores:

- `owner_type`: `job` or `application`
- `owner_id`: UUID of the owning job/application
- `source`: `jd` or `cv`
- `section`
- `chunk_text`
- `embedding`: `Vector(4096)`
- `metadata_json`
- `created_at`

### Migrations

Alembic has been added under `apps/api/migrations`.

Migration files present:

- `1a7642072efd_initial_schema.py`: empty initial migration with `pass`.
- `38289d6e6f86_add_document_chunks.py`: creates `document_chunks`, enables `vector`, and originally used `Vector(2048)`.
- `3e4e86fbbe64_change_document_chunk_embedding_.py`: deletes existing chunks and changes `document_chunks.embedding` to `vector(4096)` for Scaleway `qwen3-embedding-8b`.
- `6be302d65b1a_create_missing_app_tables.py`: creates the main app tables (`companies`, `users`, `jobs`, `applications`, chat, notifications, interviews, agent runs).

`docs/alembic.md` explains Alembic usage, but note it still mentions `Vector(2048)` in the pgvector notes. The current model and latest migration use `Vector(4096)`.

### Database Caveats

- `apps/api/app/db.py` and `apps/api/app/models.py` no longer exist.
- `apps/api/app/db_migrate.py` is stale: it imports `app.db` and `app.models`, which no longer exist.
- The current migration path should be Alembic, not `Base.metadata.create_all()`.
- `apps/api/package.json` has `db:migrate` as `PYTHONPATH=../../packages/backend_shared/talent_core ../../.venv/bin/alembic upgrade head`; verify this path in the local shell because importing `talent_core` usually requires `PYTHONPATH=../../packages/backend_shared`.

## API Surface Implemented

The FastAPI app is in `apps/api/app/main.py`, runs on port `4000`, and now has CORS enabled for:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

### FE-Facing HTTP API

| Method | Path | Implemented In | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | `apps/api/app/routers/health.py` | Basic health check. |
| `POST` | `/uploads/presign` | `apps/api/app/routers/uploads.py` | Creates a Cloudflare R2/S3-compatible presigned upload URL. |
| `POST` | `/companies` | `apps/api/app/routers/companies.py` | Creates a company. |
| `GET` | `/companies/{company_id}` | `apps/api/app/routers/companies.py` | Reads one company. |
| `POST` | `/users` | `apps/api/app/routers/users.py` | Creates a local-development HR/candidate user. |
| `GET` | `/users/{user_id}` | `apps/api/app/routers/users.py` | Reads one user. |
| `POST` | `/jobs` | `apps/api/app/routers/jobs.py` | Creates a job linked to a company. |
| `GET` | `/jobs/{job_id}` | `apps/api/app/routers/jobs.py` | Reads one job. |
| `POST` | `/applications` | `apps/api/app/routers/applications.py` | Creates an application and enqueues `agent.cv_screening`. |
| `GET` | `/applications/{application_id}` | `apps/api/app/routers/applications.py` | Reads one application. |
| `POST` | `/applications/{application_id}/submit-test` | `apps/api/app/routers/applications.py` | Stores test submission fields and attempts to enqueue `agent.assessment`. |
| `GET` | `/agent_runs/{agent_run_id}` | `apps/api/app/routers/agent_runs.py` | Reads one agent run audit record. |

### Queue / Agent API

- `apps/api/app/queue.py` exposes `enqueue(task_name, payload)`.
- `TASK_TO_QUEUE` still routes only `agent.cv_screening`.
- `submit_test()` still calls `enqueue("agent.assessment", ...)`, but `agent.assessment` is not in `TASK_TO_QUEUE`, so this path will raise unless routing is added.
- `apps/api/scripts/publish_application.py` can manually enqueue `agent.cv_screening` for a provided `application_id`.
- The worker currently implements only `agent.cv_screening`.

### R2 Upload API

Implemented upload flow:

```text
Frontend calls POST /uploads/presign
API validates upload kind
API creates sanitized object key
API creates boto3 S3-compatible Cloudflare R2 client
API returns object_key + upload_url + expires_in_seconds
Frontend uploads directly to R2 using upload_url
Frontend sends object_key to another API endpoint such as POST /applications
```

Allowed upload kinds:

- `cv`
- `test-submission`
- `job-asset`
- `interview-audio`
- `transcript`

### Frontend API Status

- The Next.js app still appears mostly static/scaffolded.
- `apps/web/app/page.tsx` now contains a job/CV screening demo-style page referencing backend AI engineer requirements, pgvector, RAG, and agent workflows.
- `apps/web/app/dashboard/hr/page.tsx` is still a static HR dashboard mock using shared status labels.
- No frontend `fetch()`/API client integration was found.

## Webcrawl / Public Evidence Status

There is still no general webcrawl/crawler HTTP API or job ingestion crawler route.

What does exist now:

- `apps/worker/app/tools/web_search.py` provides Tavily search helpers.
- It extracts public URLs from CV text, classifies GitHub/LinkedIn/portfolio links, extracts project/company targets, and verifies candidate evidence targets.
- `apps/worker/app/tools/evidence.py` verifies GitHub repository URLs via the GitHub API and uses Tavily for other candidate targets.
- `apps/worker/app/tools/evidence_review.py` implements a bounded ReAct-style evidence reviewer that may call Tavily only for unresolved candidate targets.

So “webcrawl” is implemented only as bounded public evidence verification inside CV screening, not as a standalone crawler/API.

## Current LangGraph Workflow

### What Is Implemented

The currently implemented LangGraph workflow is still the CV screening flow in `apps/worker/app/orchestration/cv_screening_graph.py`, but it has expanded substantially.

Implemented behavior:

- API creates an `Application` with `status = pending_cv`.
- API enqueues `agent.cv_screening` with `{"application_id": "<uuid>"}`.
- Worker task calls `run_cv_screening_graph(application_id)`.
- Graph loads application/job context through SQLAlchemy (`talent_core`) via `apps/worker/app/tools/db.py`.
- Graph downloads the CV object from private Cloudflare R2 and parses PDF/DOCX/text bytes.
- Graph cleans CV text.
- Graph extracts a CV profile with deterministic parsing and optional LLM refinement.
- Graph extracts a JD rubric from `scorecard_json` or a default rubric.
- Graph chunks CV and rubric/JD text.
- Graph calls an OpenAI-compatible embeddings provider and expects 4096-dimensional embeddings.
- Graph writes CV/JD chunks to `document_chunks` with pgvector embeddings.
- Graph retrieves rubric-to-CV evidence through cosine similarity search.
- Graph verifies candidate public evidence through GitHub/Tavily.
- Graph scores the CV against the rubric.
- Graph runs a bounded ReAct-style evidence review over unresolved public evidence targets.
- Graph saves an `agent_runs` audit row and updates the application with `cv_score`, `detailed_score_json`, and `cv_passed`/`cv_failed`.

### Flow Diagram

```text
POST /applications
  -> create Application(status="pending_cv")
  -> enqueue Celery task "agent.cv_screening"
  -> worker task cv_screening(payload)
  -> run_cv_screening_graph(application_id)

LangGraph StateGraph:

START
  |
  v
load_context
  - Load application, job_id, cv_object_key, jd_text, scorecard_json
  |
  v
load_cv_text
  - Download private R2 object
  - Parse PDF/DOCX/text into raw_cv_text
  |
  v
clean_cv_text
  - Normalize parsed CV text while preserving URLs and section boundaries
  |
  v
extract_cv_profile
  - Deterministically parse links, skills, projects, experience, education
  - Optionally refine with LLM JSON output
  |
  v
extract_jd_rubric
  - Use job scorecard criteria if present
  - Otherwise use default backend/worker/RAG/agent/deployment rubric
  |
  v
chunk_documents
  - Chunk cleaned CV
  - Convert rubric criteria into JD chunks
  |
  v
embed_and_index
  - Call embeddings provider
  - Replace document_chunks for application CV and job JD
  |
  v
retrieve_rubric_evidence
  - For each JD/rubric embedding, retrieve similar CV chunks from pgvector
  - Convert matches into evidence records
  |
  v
verify_public_evidence
  - Extract CV links/project/company targets
  - Verify GitHub repos or use Tavily for public evidence
  |
  v
score_rubric
  - Score each rubric criterion from claimed/retrieved/verified evidence
  - Produce cv_score, decision, decision_band, reasons, gap_analysis
  |
  v
react_review_unresolved_evidence
  - Bounded LLM ReAct reviewer may search unresolved allowed targets
  - Produces review_notes, risk_flags, external_evidence, react_steps
  |
  v
persist_result
  - Insert agent_runs audit record
  - Update application CV score, detailed output JSON, and status
  |
  v
END
```

### Graph State

The state is defined in `apps/worker/app/orchestration/state.py` as `CVScreeningState`.

Key fields include:

- application/job input: `application_id`, `job_id`, `cv_object_key`, `jd_text`, `scorecard_json`
- parsed text/profile: `raw_cv_text`, `cv_text`, `cv_profile`, `candidate_profile`
- rubric/chunks/embeddings: `jd_rubric`, `cv_chunks`, `jd_chunks`, `cv_embeddings`, `jd_embeddings`
- evidence: `retrieved_evidence`, `evidence`, `candidate_targets`, `candidate_evidence`, `external_evidence`
- scoring: `criterion_scores`, `cv_score`, `decision`, `decision_band`, `reasons`, `gap_analysis`
- review/debug: `review_notes`, `risk_flags`, `react_steps`, `tool_trace`, `errors`

### Runtime Configuration Required

The expanded graph requires these worker settings when running real CV screening:

- R2: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`
- LLM: `LLM_BASE_URL`, `LLM_API_KEY`, `MODEL_NAME`
- embeddings: `EMBEDDING_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL_NAME`, `EMBEDDING_DIMENSION`
- public evidence search: `TAVILY_API_KEY` if Tavily verification should run

Defaults in `apps/worker/app/config.py`:

- LLM base URL: `https://api.groq.com/openai/v1`
- model: `llama-3.3-70b-versatile`
- embedding base URL: `https://api.scaleway.ai/v1`
- embedding model: `qwen3-embedding-8b`
- embedding dimension: `4096`

## File Summaries

### Shared Backend Python Files

- `packages/backend_shared/talent_core/__init__.py`: Package marker for shared backend code.
- `packages/backend_shared/talent_core/config.py`: Defines shared database settings loaded from the repository `.env`. Contains `Settings`, `settings`, and SQLAlchemy/psycopg URL helpers.
- `packages/backend_shared/talent_core/db.py`: Owns SQLAlchemy `Base`, `engine`, `SessionLocal`, and `get_db()`.
- `packages/backend_shared/talent_core/models.py`: Current canonical ORM model file. Contains app enums, ATS tables, `DocumentChunk` with `Vector(4096)`, and relationships.

### API Python Files

- `apps/api/app/__init__.py`: Package marker for the FastAPI application.
- `apps/api/app/main.py`: Creates the FastAPI app, configures CORS for local web origins, and registers all routers.
- `apps/api/app/config.py`: API-specific settings for RabbitMQ, Celery result backend, R2, and database URL conversion.
- `apps/api/app/db_migrate.py`: Stale direct `create_all()` script that still imports removed `app.db`/`app.models`.
- `apps/api/app/celery_app.py`: Configures API-side Celery client, direct exchange, dead-letter queue, and `agent.cv_screening` route.
- `apps/api/app/queue.py`: Maps task names to queues and sends Celery tasks. Currently only `agent.cv_screening` is configured.
- `apps/api/app/routers/health.py`: Defines `GET /health`.
- `apps/api/app/routers/uploads.py`: Defines `POST /uploads/presign`; validates upload kind and delegates R2 presign creation.
- `apps/api/app/routers/companies.py`: Defines company create/read endpoints using shared `talent_core` DB/models.
- `apps/api/app/routers/users.py`: Defines local-development user create/read endpoints using shared `talent_core` DB/models.
- `apps/api/app/routers/jobs.py`: Defines job create/read endpoints using shared `talent_core` DB/models.
- `apps/api/app/routers/applications.py`: Defines application create/read/test submission endpoints and enqueues agent tasks.
- `apps/api/app/routers/agent_runs.py`: Reads one `AgentRun` audit record.
- `apps/api/app/schemas/applications.py`: Pydantic request/response schemas for applications and test submissions.
- `apps/api/app/schemas/companies.py`: Pydantic request/response schemas for companies.
- `apps/api/app/schemas/jobs.py`: Pydantic request/response schemas for jobs.
- `apps/api/app/schemas/uploads.py`: Pydantic request/response schemas for presigned uploads.
- `apps/api/app/schemas/users.py`: Pydantic request/response schemas for users.
- `apps/api/app/services/storage.py`: Creates R2 presigned upload URLs via boto3.
- `apps/api/scripts/publish_application.py`: CLI helper to publish a CV screening task by application ID.
- `apps/api/migrations/env.py`: Alembic environment using `talent_core.config.settings` and `talent_core.db.Base.metadata`.
- `apps/api/migrations/versions/*.py`: Alembic revisions for document chunks/vector dimensions and app tables.

### Worker Python Files

- `apps/worker/app/__init__.py`: Package marker.
- `apps/worker/app/main.py`: Exposes `celery_app`.
- `apps/worker/app/config.py`: Worker settings for DB, RabbitMQ, R2, LLM, embeddings, and Tavily.
- `apps/worker/app/celery_app.py`: Configures worker Celery queues/routes for `agent.cv_screening` and a dead-letter queue.
- `apps/worker/app/tasks.py`: Defines `agent.cv_screening`, which calls `run_cv_screening_graph()`.
- `apps/worker/app/orchestration/state.py`: Defines the typed LangGraph state.
- `apps/worker/app/orchestration/cv_screening_graph.py`: Current multi-step CV screening graph with logging, parsing, profile extraction, rubric extraction, chunking, embeddings, pgvector retrieval, public evidence verification, rubric scoring, ReAct review, and persistence.
- `apps/worker/app/tools/chunking.py`: Splits CV/JD text into section-aware chunks suitable for embedding.
- `apps/worker/app/tools/db.py`: Loads application/job context and writes agent/application results through SQLAlchemy sessions.
- `apps/worker/app/tools/documents.py`: Parses PDF bytes with `pdfplumber`, DOCX bytes with `python-docx`, and fallback text bytes.
- `apps/worker/app/tools/embeddings.py`: Calls an OpenAI-compatible embeddings endpoint and validates embedding count/dimension.
- `apps/worker/app/tools/evidence.py`: Builds evidence records, converts vector matches to evidence, verifies GitHub repos, and verifies candidate targets through Tavily.
- `apps/worker/app/tools/evidence_review.py`: Bounded ReAct evidence reviewer using LLM JSON actions and optional Tavily searches.
- `apps/worker/app/tools/llm.py`: Calls an OpenAI-compatible chat completion endpoint and parses JSON object responses.
- `apps/worker/app/tools/profile_extraction.py`: Deterministically extracts CV profile data and optionally refines with an LLM.
- `apps/worker/app/tools/r2.py`: Downloads private R2 objects and parses them into text.
- `apps/worker/app/tools/rubric.py`: Builds a normalized JD rubric from scorecard JSON or default criteria and converts criteria to chunks.
- `apps/worker/app/tools/rubric_scoring.py`: Scores rubric criteria from evidence and computes decision bands/gap analysis.
- `apps/worker/app/tools/scoring.py`: Older skill/semantic scoring helper; still present but the current graph uses rubric scoring.
- `apps/worker/app/tools/text_cleanup.py`: Normalizes parsed document text while preserving URLs.
- `apps/worker/app/tools/vector_store.py`: Replaces and searches `document_chunks` using pgvector cosine distance.
- `apps/worker/app/tools/web_search.py`: Extracts public evidence targets from CV text and runs Tavily search.

## Database Models

Complete code from `packages/backend_shared/talent_core/models.py`:

```python
from pgvector.sqlalchemy import Vector
import enum
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# ==========================================
# 1. ENUMS (Các kiểu dữ liệu giới hạn)
# ==========================================
class UserRole(str, enum.Enum):
    hr = "hr"
    candidate = "candidate"


class ApplicationStatus(str, enum.Enum):
    pending_cv = "pending_cv"
    cv_passed = "cv_passed"
    cv_failed = "cv_failed"
    test_submitted = "test_submitted"
    test_scored = "test_scored"
    test_failed = "test_failed"
    interview_scheduled = "interview_scheduled"
    interview_completed = "interview_completed"
    interview_failed = "interview_failed"
    accepted = "accepted"


class AgentRunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


# BỔ SUNG ENUM CHO CHAT VÀ THÔNG BÁO
class SenderRole(str, enum.Enum):
    user = "user"
    agent = "agent"


class NotificationType(str, enum.Enum):
    test_unlocked = "test_unlocked"
    interview_invited = "interview_invited"
    system_alert = "system_alert"


class InterviewStatus(str, enum.Enum):
    scheduled = "scheduled"  # Đã lên lịch, chưa tới giờ
    ongoing = "ongoing"  # Đang diễn ra (HR và Ứng viên đang trong phòng Jitsi)
    completed = "completed"  # Đã phỏng vấn xong
    cancelled = "cancelled"  # Đã hủy


# ==========================================
# 2. BẢNG TÀI KHOẢN & THÔNG BÁO
# ==========================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))

    auth_provider: Mapped[str] = mapped_column(String, default="local")
    hashed_password: Mapped[str | None] = mapped_column(String)
    avatar_url: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    applications: Mapped[List["Application"]] = relationship(back_populates="candidate")
    interview_slots: Mapped[List["InterviewSlot"]] = relationship(back_populates="hr")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        back_populates="candidate"
    )


class Notification(Base):
    """Chuông thông báo góc màn hình"""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type")
    )
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="notifications")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String)
    logo_url: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    jobs: Mapped[List["Job"]] = relationship(back_populates="company")


# ==========================================
# 3. BẢNG NGHIỆP VỤ (JOB, APPLICATION & CHAT)
# ==========================================
class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)

    # Nơi lưu đề thi gốc do HR cung cấp
    test_content: Mapped[dict | list | None] = mapped_column(JSONB)
    test_object_url: Mapped[str | None] = mapped_column(String)
    scorecard_json: Mapped[dict | None] = mapped_column(JSONB)
    jd_object_url: Mapped[str | None] = mapped_column(String)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    company: Mapped[Company] = relationship(back_populates="jobs")
    applications: Mapped[List["Application"]] = relationship(back_populates="job")
    chat_sessions: Mapped[List["ChatSession"]] = relationship(back_populates="job")


class ChatSession(Base):
    """Phiên chat hỏi đáp JD giữa 1 Candidate và 1 Job"""

    __tablename__ = "chat_sessions"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    candidate: Mapped[User] = relationship(back_populates="chat_sessions")
    job: Mapped[Job] = relationship(back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="session",
        order_by="ChatMessage.created_at",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    """Từng dòng tin nhắn trong phiên chat"""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id")
    )

    sender_role: Mapped[SenderRole] = mapped_column(
        Enum(SenderRole, name="sender_role")
    )
    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    # Nơi lưu Bài làm và Đề riêng của ứng viên
    cv_object_key: Mapped[str | None] = mapped_column(String)
    dynamic_test_content: Mapped[dict | list | None] = mapped_column(
        JSONB
    )  # Nội dung đề do AI tự sinh
    test_submission_url: Mapped[list[str] | None] = mapped_column(
        JSONB
    )  # Link các file nộp bài
    test_answer: Mapped[dict | list | None] = mapped_column(JSONB)  # Text nộp bài
    interview_audio_url: Mapped[str | None] = mapped_column(String)
    interview_transcript: Mapped[dict | list | None] = mapped_column(JSONB)

    # Scoring & Feedback
    cv_score: Mapped[float | None] = mapped_column(Float)
    total_score: Mapped[float | None] = mapped_column(Float)
    interview_score: Mapped[float | None] = mapped_column(Float)
    detailed_score_json: Mapped[dict | None] = mapped_column(JSONB)

    test_deadline: Mapped[datetime | None] = mapped_column(DateTime)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.pending_cv,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    candidate: Mapped[User] = relationship(back_populates="applications")
    job: Mapped[Job] = relationship(back_populates="applications")
    agent_runs: Mapped[List["AgentRun"]] = relationship(back_populates="application")
    interview_meeting: Mapped["InterviewSlot | None"] = relationship(
        back_populates="application"
    )


# ==========================================
# 4. BẢNG HỖ TRỢ (LỊCH PHỎNG VẤN & LOG AI)
# ==========================================
class InterviewSlot(Base):
    __tablename__ = "interview_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    hr_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id"), nullable=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime)

    # 1. Tên phòng Jitsi: Chỉ lưu chuỗi định danh (VD: "ai_interview_550e8400-e29b...")
    jitsi_room_name: Mapped[str] = mapped_column(String, unique=True)

    # 2. Mật khẩu phòng (Tùy chọn): Jitsi cho phép set pass qua JS, lưu sẵn ở đây để cấp cho ứng viên
    room_password: Mapped[str | None] = mapped_column(String)

    # 3. Trạng thái buổi phỏng vấn
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus, name="interview_status"),
        default=InterviewStatus.scheduled,
    )
    # ==========================================

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hr: Mapped["User"] = relationship(back_populates="interview_slots")
    application: Mapped["Application"] = relationship(
        back_populates="interview_meeting"
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id")
    )
    agent_type: Mapped[str] = mapped_column(String)
    input_json: Mapped[dict] = mapped_column(JSONB)
    output_json: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, name="agent_run_status")
    )
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    application: Mapped["Application"] = relationship(back_populates="agent_runs")


class DocumentOwnerType(str, enum.Enum):
    job = "job"
    application = "application"


class DocumentChunkSource(str, enum.Enum):
    jd = "jd"
    cv = "cv"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    owner_type: Mapped[DocumentOwnerType] = mapped_column(
        Enum(DocumentOwnerType, name="document_owner_type"), index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    source: Mapped[DocumentChunkSource] = mapped_column(
        Enum(DocumentChunkSource, name="document_chunk_source"), index=True
    )

    section: Mapped[str | None] = mapped_column(String)
    chunk_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(4096))
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

## Current LangGraph Workflow Code

Complete code from `apps/worker/app/orchestration/cv_screening_graph.py`:

```python
import logging
from functools import wraps
from time import perf_counter
from uuid import UUID

from langgraph.graph import END, StateGraph

from talent_core.models import DocumentChunkSource, DocumentOwnerType

from app.orchestration.state import CVScreeningState
from app.tools.chunking import chunk_document
from app.tools.db import (
    load_application_context,
    save_agent_run,
    update_cv_screening_result,
)
from app.tools.embeddings import embed_texts
from app.tools.evidence import (
    claimed_evidence_from_profile,
    retrieved_evidence_from_matches,
    verify_candidate_targets,
)
from app.tools.evidence_review import review_evidence_with_react
from app.tools.profile_extraction import extract_cv_profile
from app.tools.r2 import load_r2_text_object
from app.tools.rubric import criterion_chunks, extract_jd_rubric
from app.tools.rubric_scoring import score_rubric
from app.tools.text_cleanup import clean_document_text
from app.tools.vector_store import replace_document_chunks, search_similar_chunks

logger = logging.getLogger(__name__)


def trace(
    state: CVScreeningState,
    tool: str,
    input_summary: str,
    output_summary: str,
    error: str | None = None,
) -> list[dict]:
    return state["tool_trace"] + [
        {
            "tool": tool,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "error": error,
        }
    ]


def logged_node(name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(state: CVScreeningState) -> CVScreeningState:
            started_at = perf_counter()
            logger.info(
                "cv_screening.%s.start application_id=%s job_id=%s errors=%d",
                name,
                state["application_id"],
                state.get("job_id"),
                len(state.get("errors", [])),
            )
            try:
                next_state = func(state)
            except Exception:
                logger.exception(
                    "cv_screening.%s.exception application_id=%s job_id=%s elapsed_ms=%.1f",
                    name,
                    state["application_id"],
                    state.get("job_id"),
                    (perf_counter() - started_at) * 1000,
                )
                raise

            latest_trace = (
                next_state.get("tool_trace", [])[-1]
                if next_state.get("tool_trace")
                else {}
            )
            logger.info(
                "cv_screening.%s.finish application_id=%s job_id=%s elapsed_ms=%.1f errors=%d output=%s error=%s",
                name,
                next_state["application_id"],
                next_state.get("job_id"),
                (perf_counter() - started_at) * 1000,
                len(next_state.get("errors", [])),
                latest_trace.get("output_summary"),
                latest_trace.get("error"),
            )
            return next_state

        return wrapper

    return decorator


@logged_node("load_context")
def load_context(state: CVScreeningState) -> CVScreeningState:
    context = load_application_context(state["application_id"])
    return {
        **state,
        "job_id": context["job_id"],
        "cv_object_key": context["cv_object_key"],
        "jd_text": context["jd_text"],
        "scorecard_json": context["scorecard_json"],
        "tool_trace": trace(
            state,
            "load_context",
            state["application_id"],
            f"loaded job_id={context['job_id']}",
        ),
    }


@logged_node("load_cv_text")
def load_cv_text(state: CVScreeningState) -> CVScreeningState:
    cv_object_key = state["cv_object_key"]
    if not cv_object_key:
        error = "Application has no cv_object_key"
        return {
            **state,
            "errors": state["errors"] + [error],
            "tool_trace": trace(state, "load_cv_text", "missing key", "skipped", error),
        }

    raw_cv_text = load_r2_text_object(cv_object_key)
    return {
        **state,
        "raw_cv_text": raw_cv_text,
        "tool_trace": trace(
            state,
            "load_cv_text",
            cv_object_key,
            f"loaded {len(raw_cv_text)} characters",
        ),
    }


@logged_node("clean_cv_text")
def clean_cv_text(state: CVScreeningState) -> CVScreeningState:
    cleaned = clean_document_text(state["raw_cv_text"] or "")
    return {
        **state,
        "cv_text": cleaned,
        "tool_trace": trace(
            state,
            "clean_cv_text",
            "raw_cv_text",
            f"cleaned {len(cleaned)} characters",
        ),
    }


@logged_node("extract_cv_profile")
def extract_profile(state: CVScreeningState) -> CVScreeningState:
    profile, error = extract_cv_profile(state["cv_text"] or "")
    errors = state["errors"] + ([f"CV profile fallback used: {error}"] if error else [])
    return {
        **state,
        "cv_profile": profile,
        "candidate_profile": profile,
        "errors": errors,
        "tool_trace": trace(
            state,
            "extract_cv_profile",
            "cv_text",
            f"projects={len(profile.get('projects', []))}, experience={len(profile.get('experience', []))}, source={profile.get('extraction_source')}",
            error,
        ),
    }


@logged_node("extract_jd_rubric")
def extract_rubric(state: CVScreeningState) -> CVScreeningState:
    jd_rubric = extract_jd_rubric(state["jd_text"], state["scorecard_json"])
    return {
        **state,
        "jd_rubric": jd_rubric,
        "tool_trace": trace(
            state,
            "extract_jd_rubric",
            "jd_text + scorecard_json",
            f"criteria={len(jd_rubric.get('criteria', []))}",
        ),
    }


@logged_node("chunk_documents")
def chunk_documents(state: CVScreeningState) -> CVScreeningState:
    cv_chunks = chunk_document(state["cv_text"] or "", source="cv")
    jd_chunks = criterion_chunks(state["jd_rubric"] or {})
    if not jd_chunks:
        jd_chunks = chunk_document(state["jd_text"], source="jd")

    errors = list(state["errors"])
    if not cv_chunks:
        errors.append("CV produced no chunks")
    if not jd_chunks:
        errors.append("JD produced no chunks")

    return {
        **state,
        "cv_chunks": cv_chunks,
        "jd_chunks": jd_chunks,
        "errors": errors,
        "tool_trace": trace(
            state,
            "chunk_documents",
            "cv_profile + jd_rubric",
            f"cv_chunks={len(cv_chunks)}, jd_chunks={len(jd_chunks)}",
        ),
    }


@logged_node("embed_and_index")
def embed_and_index(state: CVScreeningState) -> CVScreeningState:
    if not state["job_id"] or not state["cv_chunks"] or not state["jd_chunks"]:
        return {
            **state,
            "tool_trace": trace(
                state,
                "embed_and_index",
                "chunks",
                "skipped because required chunks/job_id are missing",
            ),
        }

    try:
        cv_embeddings = embed_texts(
            [chunk["text"] for chunk in state["cv_chunks"]], input_type="passage"
        )
        jd_embeddings = embed_texts(
            [chunk["text"] for chunk in state["jd_chunks"]], input_type="passage"
        )
        replace_document_chunks(
            owner_type=DocumentOwnerType.application,
            owner_id=UUID(state["application_id"]),
            source=DocumentChunkSource.cv,
            chunks=state["cv_chunks"],
            embeddings=cv_embeddings,
        )
        replace_document_chunks(
            owner_type=DocumentOwnerType.job,
            owner_id=UUID(state["job_id"]),
            source=DocumentChunkSource.jd,
            chunks=state["jd_chunks"],
            embeddings=jd_embeddings,
        )
        return {
            **state,
            "cv_embeddings": cv_embeddings,
            "jd_embeddings": jd_embeddings,
            "tool_trace": trace(
                state,
                "embed_and_index",
                "cv_chunks + jd_chunks",
                f"indexed {len(cv_embeddings)} CV and {len(jd_embeddings)} JD embeddings",
            ),
        }
    except Exception as exc:
        error = f"Embedding/indexing failed: {exc}"
        return {
            **state,
            "errors": state["errors"] + [error],
            "tool_trace": trace(state, "embed_and_index", "chunks", "failed", error),
        }


@logged_node("retrieve_rubric_evidence")
def retrieve_rubric_evidence(state: CVScreeningState) -> CVScreeningState:
    if not state["jd_embeddings"]:
        return {
            **state,
            "tool_trace": trace(
                state,
                "retrieve_rubric_evidence",
                "jd_embeddings",
                "skipped because embeddings are unavailable",
            ),
        }

    matches: list[dict] = []
    for jd_chunk, jd_embedding in zip(state["jd_chunks"], state["jd_embeddings"]):
        criterion_id = (jd_chunk.get("metadata") or {}).get("criterion_id")
        for match in search_similar_chunks(
            owner_type=DocumentOwnerType.application,
            owner_id=UUID(state["application_id"]),
            source=DocumentChunkSource.cv,
            query_embedding=jd_embedding,
            limit=3,
        ):
            matches.append(
                {
                    "criterion_id": criterion_id,
                    "jd_section": jd_chunk.get("section"),
                    "jd_text": jd_chunk.get("text"),
                    "cv_section": match["section"],
                    "cv_text": match["text"],
                    "similarity": match["similarity"],
                }
            )

    matches = sorted(matches, key=lambda item: item["similarity"], reverse=True)[:18]
    retrieved_evidence = retrieved_evidence_from_matches(matches)
    return {
        **state,
        "retrieved_evidence": matches,
        "evidence": state["evidence"] + retrieved_evidence,
        "tool_trace": trace(
            state,
            "retrieve_rubric_evidence",
            "rubric embeddings -> cv index",
            f"retrieved {len(matches)} rubric evidence matches",
        ),
    }


@logged_node("verify_public_evidence")
def verify_public_evidence(state: CVScreeningState) -> CVScreeningState:
    claimed = claimed_evidence_from_profile(state["cv_profile"] or {})
    try:
        targets, public_evidence = verify_candidate_targets(
            state["cv_text"] or "", state["cv_profile"] or {}, max_targets=6
        )
        return {
            **state,
            "candidate_targets": targets,
            "candidate_evidence": public_evidence,
            "evidence": state["evidence"] + claimed + public_evidence,
            "tool_trace": trace(
                state,
                "verify_public_evidence",
                "cv links, projects, companies",
                f"targets={len(targets)}, evidence={len(public_evidence)}",
            ),
        }
    except Exception as exc:
        error = f"Candidate evidence verification failed: {exc}"
        return {
            **state,
            "evidence": state["evidence"] + claimed,
            "errors": state["errors"] + [error],
            "tool_trace": trace(
                state,
                "verify_public_evidence",
                "cv links, projects, companies",
                "failed",
                error,
            ),
        }


@logged_node("score_rubric")
def score_by_rubric(state: CVScreeningState) -> CVScreeningState:
    result = score_rubric(state["jd_rubric"] or {}, state["evidence"])
    return {
        **state,
        "cv_score": result["cv_score"],
        "decision": result["decision"],
        "decision_band": result["decision_band"],
        "criterion_scores": result["criterion_scores"],
        "reasons": result["reasons"],
        "gap_analysis": result["gap_analysis"],
        "tool_trace": trace(
            state,
            "score_rubric",
            "jd_rubric + evidence",
            f"score={result['cv_score']}, band={result['decision_band']}",
        ),
    }


@logged_node("react_review_unresolved_evidence")
def react_review_unresolved_evidence(state: CVScreeningState) -> CVScreeningState:
    try:
        review = review_evidence_with_react(state)
        return {
            **state,
            "gap_analysis": review["gap_analysis"],
            "external_evidence": review["external_evidence"],
            "review_notes": review["review_notes"],
            "risk_flags": review["risk_flags"],
            "react_steps": review["react_steps"],
            "tool_trace": trace(
                state,
                "react_review_unresolved_evidence",
                "rubric score + evidence",
                f"react_steps={len(review['react_steps'])}, external_evidence={len(review['external_evidence'])}",
            ),
        }
    except Exception as exc:
        error = f"ReAct evidence review failed: {exc}"
        return {
            **state,
            "errors": state["errors"] + [error],
            "tool_trace": trace(
                state,
                "react_review_unresolved_evidence",
                "rubric score + evidence",
                "failed",
                error,
            ),
        }


@logged_node("persist_result")
def persist_result(state: CVScreeningState) -> CVScreeningState:
    output = {
        "agent": "cv_screener",
        "job_id": state["job_id"],
        "cv_score": state["cv_score"],
        "decision": state["decision"],
        "decision_band": state["decision_band"],
        "reasons": state["reasons"],
        "gap_analysis": state["gap_analysis"],
        "candidate_profile": state["candidate_profile"],
        "cv_profile": state["cv_profile"],
        "jd_rubric": state["jd_rubric"],
        "criterion_scores": state["criterion_scores"],
        "evidence": state["evidence"],
        "retrieved_evidence": state["retrieved_evidence"],
        "candidate_targets": state["candidate_targets"],
        "candidate_evidence": state["candidate_evidence"],
        "external_evidence": state["external_evidence"],
        "review_notes": state["review_notes"],
        "risk_flags": state["risk_flags"],
        "react_steps": state["react_steps"],
        "tool_trace": state["tool_trace"],
        "errors": state["errors"],
    }

    save_agent_run(
        application_id=state["application_id"],
        agent_type="cv_screener",
        input_json={"application_id": state["application_id"]},
        output_json=output,
    )
    if state["cv_score"] is not None and state["decision"] is not None:
        update_cv_screening_result(
            application_id=state["application_id"],
            cv_score=state["cv_score"],
            decision=state["decision"],
            output=output,
        )

    return {
        **state,
        "tool_trace": trace(
            state,
            "persist_result",
            "agent_run + application",
            f"persisted={state['cv_score'] is not None}",
        ),
    }


def build_cv_screening_graph():
    graph = StateGraph(CVScreeningState)
    graph.add_node("load_context", load_context)
    graph.add_node("load_cv_text", load_cv_text)
    graph.add_node("clean_cv_text", clean_cv_text)
    graph.add_node("extract_cv_profile", extract_profile)
    graph.add_node("extract_jd_rubric", extract_rubric)
    graph.add_node("chunk_documents", chunk_documents)
    graph.add_node("embed_and_index", embed_and_index)
    graph.add_node("retrieve_rubric_evidence", retrieve_rubric_evidence)
    graph.add_node("verify_public_evidence", verify_public_evidence)
    graph.add_node("score_rubric", score_by_rubric)
    graph.add_node("react_review_unresolved_evidence", react_review_unresolved_evidence)
    graph.add_node("persist_result", persist_result)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "load_cv_text")
    graph.add_edge("load_cv_text", "clean_cv_text")
    graph.add_edge("clean_cv_text", "extract_cv_profile")
    graph.add_edge("extract_cv_profile", "extract_jd_rubric")
    graph.add_edge("extract_jd_rubric", "chunk_documents")
    graph.add_edge("chunk_documents", "embed_and_index")
    graph.add_edge("embed_and_index", "retrieve_rubric_evidence")
    graph.add_edge("retrieve_rubric_evidence", "verify_public_evidence")
    graph.add_edge("verify_public_evidence", "score_rubric")
    graph.add_edge("score_rubric", "react_review_unresolved_evidence")
    graph.add_edge("react_review_unresolved_evidence", "persist_result")
    graph.add_edge("persist_result", END)
    return graph.compile()


cv_screening_graph = build_cv_screening_graph()


def run_cv_screening_graph(application_id: str) -> dict:
    initial_state: CVScreeningState = {
        "application_id": application_id,
        "job_id": None,
        "cv_object_key": None,
        "jd_text": "",
        "scorecard_json": None,
        "raw_cv_text": None,
        "cv_text": None,
        "cv_profile": None,
        "jd_rubric": None,
        "cv_chunks": [],
        "jd_chunks": [],
        "cv_embeddings": [],
        "jd_embeddings": [],
        "retrieved_evidence": [],
        "evidence": [],
        "candidate_targets": [],
        "candidate_evidence": [],
        "external_evidence": [],
        "review_notes": [],
        "risk_flags": [],
        "react_steps": [],
        "criterion_scores": [],
        "candidate_profile": None,
        "cv_score": None,
        "decision": None,
        "decision_band": None,
        "reasons": [],
        "gap_analysis": None,
        "tool_trace": [],
        "errors": [],
    }
    return cv_screening_graph.invoke(initial_state)
```
