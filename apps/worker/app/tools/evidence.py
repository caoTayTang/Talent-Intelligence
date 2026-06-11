import re
from urllib.parse import urlparse

import httpx

from app.tools.web_search import extract_candidate_evidence_targets, tavily_search


def make_evidence(
    evidence_id: str,
    grade: str,
    source: str,
    claim: str,
    criterion_id: str | None = None,
    supporting_text: str | None = None,
    url: str | None = None,
    confidence: float = 0.0,
    notes: list[str] | None = None,
) -> dict:
    return {
        "id": evidence_id,
        "grade": grade,
        "source": source,
        "claim": claim,
        "criterion_id": criterion_id,
        "supporting_text": supporting_text,
        "url": url,
        "confidence": round(confidence, 2),
        "notes": notes or [],
    }


def claimed_evidence_from_profile(profile: dict) -> list[dict]:
    evidence: list[dict] = []
    counter = 1
    for project in profile.get("projects", []):
        evidence.append(
            make_evidence(
                f"ev_claim_{counter:03d}",
                "claimed",
                "cv",
                f"Project claim: {project.get('name')}",
                supporting_text=project.get("description"),
                confidence=0.45,
            )
        )
        counter += 1
    for job in profile.get("experience", []):
        evidence.append(
            make_evidence(
                f"ev_claim_{counter:03d}",
                "claimed",
                "cv",
                f"Experience claim: {job.get('company')}",
                supporting_text=job.get("description"),
                confidence=0.45,
            )
        )
        counter += 1
    return evidence


def retrieved_evidence_from_matches(matches: list[dict], start_index: int = 1) -> list[dict]:
    evidence: list[dict] = []
    for offset, item in enumerate(matches, start=start_index):
        evidence.append(
            make_evidence(
                f"ev_retrieved_{offset:03d}",
                "retrieved",
                "vector_retrieval",
                f"CV chunk matched criterion {item.get('criterion_id')}",
                criterion_id=item.get("criterion_id"),
                supporting_text=item.get("cv_text"),
                confidence=max(0.0, min(0.85, float(item.get("similarity") or 0))),
                notes=[f"similarity={float(item.get('similarity') or 0):.3f}"],
            )
        )
    return evidence


def parse_github_url(url: str) -> tuple[str, str] | None:
    parsed = urlparse(url)
    if "github.com" not in parsed.netloc.lower():
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def verify_github_url(url: str, evidence_id: str) -> dict:
    repo = parse_github_url(url)
    if repo is None:
        return make_evidence(
            evidence_id,
            "unsupported",
            "github",
            f"GitHub target is not a repository URL: {url}",
            url=url,
            confidence=0.1,
            notes=["Only repository URLs are verified in this pass."],
        )

    owner, name = repo
    api_url = f"https://api.github.com/repos/{owner}/{name}"
    try:
        response = httpx.get(api_url, timeout=20)
    except Exception as exc:
        return make_evidence(
            evidence_id,
            "unsupported",
            "github",
            f"GitHub repository lookup failed: {url}",
            url=url,
            confidence=0.1,
            notes=[str(exc)],
        )

    if response.status_code == 200:
        payload = response.json()
        description = payload.get("description") or ""
        language = payload.get("language") or "unknown"
        stars = payload.get("stargazers_count")
        updated_at = payload.get("updated_at")
        return make_evidence(
            evidence_id,
            "verified",
            "github",
            f"Verified GitHub repository {owner}/{name}",
            supporting_text=f"{description} Primary language: {language}. Stars: {stars}. Updated: {updated_at}.",
            url=payload.get("html_url") or url,
            confidence=0.95,
            notes=["GitHub API repository metadata matched the requested URL."],
        )

    return make_evidence(
        evidence_id,
        "unsupported",
        "github",
        f"GitHub repository was not found or unavailable: {owner}/{name}",
        url=url,
        confidence=0.1,
        notes=[f"GitHub API status={response.status_code}"],
    )


def source_matches_target(source_url: str | None, target: dict) -> bool:
    if not source_url:
        return False
    source = source_url.lower()
    label = str(target.get("label") or "").lower()
    query = str(target.get("query") or "").lower()
    if label.startswith("http") and label.rstrip("/") in source.rstrip("/"):
        return True
    if "github.com" in label and label.replace("https://", "").rstrip("/") in source:
        return True
    target_words = [word for word in re.split(r"\W+", label) if len(word) >= 4]
    return bool(target_words) and all(word in source for word in target_words[:3])


def verify_with_tavily(target: dict, evidence_id: str) -> dict:
    result = tavily_search(target["query"], max_results=3)
    matching_sources = [
        source for source in result.get("sources", []) if source_matches_target(source.get("url"), target)
    ]
    if matching_sources:
        return make_evidence(
            evidence_id,
            "verified",
            "tavily",
            f"Public source matched candidate target: {target['label']}",
            supporting_text=result.get("answer"),
            url=matching_sources[0].get("url"),
            confidence=0.7,
            notes=[f"matched_sources={len(matching_sources)}"],
        )
    return make_evidence(
        evidence_id,
        "unsupported",
        "tavily",
        f"No public source matched candidate target: {target['label']}",
        supporting_text=result.get("answer"),
        url=None,
        confidence=0.15,
        notes=["Tavily returned no source matching the requested target."],
    )


def verify_candidate_targets(cv_text: str, profile: dict, max_targets: int = 6) -> tuple[list[dict], list[dict]]:
    targets = extract_candidate_evidence_targets(cv_text, max_targets=max_targets)
    evidence: list[dict] = []
    for index, target in enumerate(targets, start=1):
        evidence_id = f"ev_public_{index:03d}"
        label = target.get("label") or ""
        if target.get("kind") == "github" and "github.com" in label:
            evidence.append(verify_github_url(label, evidence_id))
            continue
        evidence.append(verify_with_tavily(target, evidence_id))
    return targets, evidence
