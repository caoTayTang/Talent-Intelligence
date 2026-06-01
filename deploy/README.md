# Deployment Scaffold

This directory demonstrates deployment and Kubernetes design. It is intentionally a scaffold and does not deploy anything by itself.

## Components

- `web`: Next.js candidate and HR UI.
- `api`: FastAPI service for applications, uploads, and Celery task publishing.
- `worker`: Celery worker for agent jobs.
- `postgres`: external managed PostgreSQL with pgvector in production.
- `rabbitmq`: RabbitMQ broker, preferably managed or deployed as a dedicated StatefulSet/Helm chart in production.
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

For a real deployment, replace image names, wire managed PostgreSQL/RabbitMQ URLs, create secrets through your cloud secret manager, and run database migrations as a one-off job.
