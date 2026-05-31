# Talent Intelligence

Multi-agent ATS scaffold for gated recruiting workflows: CV screening, take-home assessment, interview scheduling, and transcription.

## Stack

- Web: Next.js
- API: FastAPI
- Database: PostgreSQL + pgvector
- Queue: Redis lists for the scaffolded worker
- Storage: Cloudflare R2
- ORM: SQLAlchemy

## Structure

```txt
apps/web       Candidate and HR UI
apps/api       FastAPI service, SQLAlchemy models, R2 adapter
apps/worker    Python Redis worker for agent jobs
packages/shared Shared types and state machine helpers
docs           Architecture and wireframes
```

## Getting Started

```bash
npm install
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt -r apps/worker/requirements.txt
cp .env.example .env
docker compose up -d
npm run db:generate
npm run db:migrate
npm run dev:web
```

Run the API and worker in separate terminals with the same virtual environment active:

```bash
npm run dev:api
npm run dev:worker
```

The first scaffold focuses on UI and module boundaries. Agent implementations are mocked in a Python worker so the product flow can be built before LLM behavior is finalized.
