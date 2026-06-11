import re
from urllib.parse import urlparse

import httpx

from app.config import settings

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
URL_PATTERN = re.compile(r"https?://[^\s)>,]+|(?:github|linkedin)\.com/[^\s)>,]+", re.IGNORECASE)
PROJECT_SECTION_PATTERN = re.compile(r"^(projects?|experience|work experience|employment)$", re.IGNORECASE)
SECTION_HEADING_PATTERN = re.compile(r"^#{0,3}\s*([A-Za-z][A-Za-z /&+-]{1,40}):?$")
GENERIC_EVIDENCE_WORDS = {
    "python",
    "fastapi",
    "sqlalchemy",
    "postgresql",
    "postgres",
    "pgvector",
    "rabbitmq",
    "celery",
    "langgraph",
    "rag",
    "docker",
    "kubernetes",
    "aws",
    "react",
    "next.js",
}


class TavilySearchError(RuntimeError):
    pass


def tavily_search(query: str, max_results: int = 3) -> dict:
    """
    Run one Tavily search and return a compact, log-safe result.
    """
    if not settings.tavily_api_key:
        return {"query": query, "answer": None, "sources": []}

    response = httpx.post(
        TAVILY_SEARCH_URL,
        json={
            "api_key": settings.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": True,
        },
        timeout=20,
    )

    if response.status_code >= 400:
        raise TavilySearchError(
            f"Tavily search failed with HTTP {response.status_code}: {response.text[:300]}"
        )

    payload = response.json()
    return {
        "query": query,
        "answer": payload.get("answer"),
        "sources": [
            {
                "title": item.get("title"),
                "url": item.get("url"),
            }
            for item in payload.get("results", [])[:max_results]
        ],
    }


def normalize_url(raw_url: str) -> str:
    url = raw_url.rstrip(".,;]")
    if not url.startswith("http"):
        url = "https://" + url
    return url


def classify_url(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "github.com" in host:
        return "github"
    if "linkedin.com" in host:
        return "linkedin"
    return "portfolio"


def extract_public_urls(cv_text: str) -> list[dict]:
    seen: set[str] = set()
    targets: list[dict] = []
    for match in URL_PATTERN.finditer(cv_text):
        url = normalize_url(match.group(0))
        if url in seen:
            continue
        seen.add(url)
        targets.append(
            {
                "kind": classify_url(url),
                "label": url,
                "query": url,
            }
        )
    return targets


def clean_candidate_name(line: str) -> str:
    name = re.sub(r"^[-*\d.)\s]+", "", line).strip()
    name = re.split(r"\s[-|:]\s", name, maxsplit=1)[0].strip()
    return name[:80]


def looks_like_public_evidence_name(name: str) -> bool:
    normalized = name.lower().strip()
    if not normalized or normalized in GENERIC_EVIDENCE_WORDS:
        return False
    if name.endswith("."):
        return False
    if len(normalized) < 4 or len(normalized.split()) > 8:
        return False
    return any(char.isupper() for char in name) or any(char.isdigit() for char in name)


def extract_project_company_targets(cv_text: str, max_targets: int = 4) -> list[dict]:
    targets: list[dict] = []
    seen: set[str] = set()
    active_section = "other"

    for raw_line in cv_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading_match = SECTION_HEADING_PATTERN.match(line.strip("# "))
        if heading_match:
            heading = heading_match.group(1).strip().lower()
            active_section = heading
            continue

        if not PROJECT_SECTION_PATTERN.match(active_section):
            continue

        name = clean_candidate_name(line)
        if not looks_like_public_evidence_name(name):
            continue

        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        targets.append(
            {
                "kind": "project_or_company",
                "label": name,
                "query": f'"{name}" GitHub OR LinkedIn OR portfolio',
            }
        )
        if len(targets) >= max_targets:
            break

    return targets


def extract_candidate_evidence_targets(cv_text: str, max_targets: int = 6) -> list[dict]:
    targets = extract_public_urls(cv_text)
    remaining = max(0, max_targets - len(targets))
    if remaining:
        targets.extend(extract_project_company_targets(cv_text, max_targets=remaining))
    return targets[:max_targets]


def verify_candidate_public_evidence(cv_text: str, max_searches: int = 4) -> list[dict]:
    """
    Verify candidate-owned public evidence from CV links, projects, or companies.
    This intentionally does not search generic skills or missing JD terms.
    """
    if not cv_text or not settings.tavily_api_key:
        return []

    verified: list[dict] = []
    for target in extract_candidate_evidence_targets(cv_text, max_targets=max_searches):
        result = tavily_search(target["query"], max_results=3)
        verified.append(
            {
                "kind": target["kind"],
                "label": target["label"],
                "query": target["query"],
                "answer": result.get("answer"),
                "sources": result.get("sources", []),
            }
        )

    return verified
