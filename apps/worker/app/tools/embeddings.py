import httpx

from app.config import settings


class EmbeddingError(RuntimeError):
    pass


def _embeddings_url() -> str:
    return settings.embedding_base_url.rstrip("/") + "/embeddings"


def embed_texts(texts: list[str], input_type: str = "passage") -> list[list[float]]:
    """
    Embed texts with an OpenAI-compatible embeddings provider.
    """
    if not texts:
        return []

    if not settings.embedding_api_key:
        raise EmbeddingError("EMBEDDING_API_KEY is not configured")

    payload = {
        "model": settings.embedding_model_name,
        "input": texts,
    }
    if "scaleway.ai" not in settings.embedding_base_url:
        payload["input_type"] = input_type

    response = httpx.post(
        _embeddings_url(),
        headers={
            "Authorization": f"Bearer {settings.embedding_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=45,
    )

    if response.status_code >= 400:
        raise EmbeddingError(
            f"Embeddings request failed with HTTP {response.status_code}: {response.text[:300]}"
        )

    response_payload = response.json()
    embeddings = [item["embedding"] for item in response_payload.get("data", [])]

    if len(embeddings) != len(texts):
        raise EmbeddingError("Provider returned a different number of embeddings than inputs")

    for embedding in embeddings:
        if len(embedding) != settings.embedding_dimension:
            raise EmbeddingError(
                f"Expected {settings.embedding_dimension}-dim embedding, got {len(embedding)}"
            )

    return embeddings

