# Deployment Scaffold

This directory is for demonstrating deployment and Kubernetes design skills. It is intentionally a scaffold and does not deploy anything by itself.

## Components

- `web`: Next.js candidate and HR UI.
- `api`: FastAPI service for applications, uploads, queue publishing, and scheduling.
- `worker`: Python Redis-list consumers for agent jobs.
- `postgres`: external managed Postgres with pgvector in production.
- `redis`: external managed Redis in production.
- `r2`: Cloudflare R2 for CVs, test submissions, job assets, and transcripts.

## Image Build Examples

```bash
docker build -f apps/web/Dockerfile -t talent-web:dev .
docker build -f apps/api/Dockerfile -t talent-api:dev .
docker build -f apps/worker/Dockerfile -t talent-worker:dev .
```

## Kubernetes Layout

```txt
deploy/k8s/base
  namespace.yaml
  configmap.yaml
  secret.example.yaml
  web.yaml
  api.yaml
  worker.yaml
  ingress.yaml
```

For a real deployment, replace image names, wire managed Postgres/Redis URLs, create secrets through your cloud secret manager, and run database migrations as a one-off job.
