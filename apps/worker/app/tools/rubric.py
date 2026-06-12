import re

from app.tools.scoring import extract_skills

DEFAULT_CRITERIA = [
    {
        "id": "backend_api_orm",
        "label": "Backend API and ORM depth",
        "weight": 25,
        "signals": ["FastAPI", "SQLAlchemy", "PostgreSQL", "Alembic"],
    },
    {
        "id": "async_workers",
        "label": "Async worker and queue experience",
        "weight": 20,
        "signals": ["RabbitMQ", "Celery", "retry", "DLQ"],
    },
    {
        "id": "rag_vectors",
        "label": "RAG and vector database experience",
        "weight": 20,
        "signals": ["RAG", "pgvector", "embeddings", "semantic search"],
    },
    {
        "id": "agent_orchestration",
        "label": "Agent orchestration experience",
        "weight": 15,
        "signals": ["LangGraph", "ReAct", "tool calling", "evidence review"],
    },
    {
        "id": "deployment",
        "label": "Deployment and DevOps experience",
        "weight": 10,
        "signals": ["Docker", "Kubernetes", "AWS", "GitHub Actions"],
    },
    {
        "id": "communication",
        "label": "Communication and evidence quality",
        "weight": 10,
        "signals": ["clear project evidence", "structured explanations"],
    },
]


def normalize_criterion(raw: dict, index: int) -> dict:
    label = raw.get("label") or raw.get("name") or f"Criterion {index + 1}"
    criterion_id = raw.get("id") or re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    signals = raw.get("signals") or raw.get("skills") or []
    return {
        "id": criterion_id,
        "label": label,
        "weight": float(raw.get("weight", 0)),
        "signals": [str(signal) for signal in signals],
        "evidence_queries": raw.get("evidence_queries") or [label] + [str(s) for s in signals],
    }


def extract_jd_rubric(jd_text: str, scorecard_json: dict | None) -> dict:
    raw_criteria = []
    if scorecard_json and isinstance(scorecard_json, dict):
        raw_criteria = scorecard_json.get("criteria") or []

    criteria = [normalize_criterion(item, index) for index, item in enumerate(raw_criteria)]
    if not criteria:
        criteria = [normalize_criterion(item, index) for index, item in enumerate(DEFAULT_CRITERIA)]

    total_weight = sum(item["weight"] for item in criteria) or 1
    for item in criteria:
        item["weight"] = round((item["weight"] / total_weight) * 100, 2)

    return {
        "role_title": None,
        "required_skills": extract_skills(jd_text),
        "nice_to_have_skills": [],
        "criteria": criteria,
    }


def criterion_chunks(jd_rubric: dict) -> list[dict]:
    chunks = []
    for criterion in jd_rubric.get("criteria", []):
        text = " ".join(
            [criterion.get("label", "")]
            + criterion.get("signals", [])
            + criterion.get("evidence_queries", [])
        ).strip()
        chunks.append(
            {
                "source": "jd",
                "section": "rubric",
                "text": text,
                "metadata": {
                    "unit_type": "criterion",
                    "criterion_id": criterion["id"],
                    "subsection": criterion["label"],
                },
            }
        )
    return chunks
