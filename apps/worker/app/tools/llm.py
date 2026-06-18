import json
import re

import httpx

from app.config import settings


class LLMError(RuntimeError):
    pass


def _chat_url() -> str:
    return settings.llm_base_url.rstrip("/") + "/chat/completions"


def _parse_json_object(content: str) -> dict:
    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def chat_json(messages: list[dict], temperature: float = 0.1) -> dict:
    """
    Call an OpenAI-compatible chat provider and parse a JSON object response.
    """
    if not settings.llm_api_key:
        raise LLMError("LLM_API_KEY is not configured")
    if not settings.model_name:
        raise LLMError("MODEL_NAME is not configured")

    response = httpx.post(
        _chat_url(),
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.model_name,
            "messages": messages,
            "temperature": temperature,
        },
        timeout=45,
    )

    if response.status_code >= 400:
        raise LLMError(
            f"LLM chat failed with HTTP {response.status_code}: {response.text[:300]}"
        )

    content = response.json()["choices"][0]["message"]["content"]
    try:
        return _parse_json_object(content)
    except json.JSONDecodeError as exc:
        raise LLMError(f"LLM returned non-JSON content: {content[:300]}") from exc
