FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.9.6 /uv /usr/local/bin/uv
COPY apps/api/requirements.txt ./requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

COPY apps/api/app ./app

EXPOSE 4000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]
