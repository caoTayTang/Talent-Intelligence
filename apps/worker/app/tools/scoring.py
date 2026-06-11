import re

SKILL_KEYWORDS = {
    "python",
    "fastapi",
    "django",
    "sqlalchemy",
    "postgresql",
    "postgres",
    "pgvector",
    "docker",
    "kubernetes",
    "k8s",
    "rabbitmq",
    "celery",
    "langgraph",
    "llm",
    "rag",
    "pytorch",
    "tensorflow",
    "react",
    "next.js",
    "typescript",
    "aws",
    "r2",
    "openrouter",
}

SKILL_ALIASES = {
    "postgres": "postgresql",
    "k8s": "kubernetes",
}


def normalize(text: str) -> str:
    return text.lower()


def canonical_skill(skill: str) -> str:
    return SKILL_ALIASES.get(skill, skill)


def extract_skills(text: str) -> list[str]:
    normalized = normalize(text)
    found = []

    for skill in SKILL_KEYWORDS:
        if skill in normalized:
            found.append(canonical_skill(skill))

    return sorted(set(found))


def estimate_years_experience(text: str) -> int | None:
    patterns = [
        r"(\d+)\+?\s+years",
        r"(\d+)\+?\s+year",
        r"(\d+)\+?\s+yrs",
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))

    return None


def semantic_score_from_evidence(retrieved_evidence: list[dict]) -> float | None:
    similarities = [
        float(item["similarity"])
        for item in retrieved_evidence
        if item.get("similarity") is not None
    ]
    if not similarities:
        return None

    top = sorted(similarities, reverse=True)[:5]
    return round((sum(top) / len(top)) * 100, 2)


def build_gap_analysis(
    matched_skills: list[str],
    missing_skills: list[str],
    semantic_score: float | None,
    years_experience: int | None,
) -> str:
    parts = []
    if matched_skills:
        parts.append(f"Strongest matching signals: {', '.join(matched_skills[:8])}.")
    if missing_skills:
        parts.append(f"Primary gaps against the JD: {', '.join(missing_skills[:8])}.")
    if semantic_score is not None:
        parts.append(
            f"Retrieved CV/JD evidence similarity is {semantic_score:.1f}/100."
        )
    if years_experience is not None:
        parts.append(f"Detected approximately {years_experience} years of experience.")

    return (
        " ".join(parts)
        if parts
        else "Insufficient evidence to produce a detailed gap analysis."
    )


def score_cv_against_jd(
    cv_text: str,
    jd_text: str,
    retrieved_evidence: list[dict] | None = None,
    candidate_evidence: list[dict] | None = None,
    scorecard_json: dict | None = None,
) -> dict:
    cv_skills = extract_skills(cv_text)
    jd_skills = extract_skills(jd_text)
    retrieved_evidence = retrieved_evidence or []
    candidate_evidence = candidate_evidence or []

    if not jd_skills:
        skill_score = 50.0
        matched_skills = []
        missing_skills = []
    else:
        matched_skills = sorted(set(cv_skills) & set(jd_skills))
        missing_skills = sorted(set(jd_skills) - set(cv_skills))
        skill_score = round((len(matched_skills) / len(jd_skills)) * 100, 2)

    years_experience = estimate_years_experience(cv_text)
    experience_score = 65.0 if years_experience is not None else 40.0
    semantic_score = semantic_score_from_evidence(retrieved_evidence)

    if semantic_score is None:
        cv_score = round((skill_score * 0.8) + (experience_score * 0.2), 2)
    else:
        cv_score = round(
            (skill_score * 0.5) + (semantic_score * 0.35) + (experience_score * 0.15),
            2,
        )

    decision = "pass" if cv_score >= 60 else "fail"
    gap_analysis = build_gap_analysis(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        semantic_score=semantic_score,
        years_experience=years_experience,
    )

    reasons = [
        f"Matched {len(matched_skills)} of {len(jd_skills)} required skill signals.",
        f"Skill score: {skill_score:.1f}/100.",
    ]
    if semantic_score is not None:
        reasons.append(f"Semantic evidence score: {semantic_score:.1f}/100.")
    if candidate_evidence:
        reasons.append(
            f"Verified {len(candidate_evidence)} candidate public evidence targets with Tavily."
        )
    if scorecard_json:
        reasons.append("Job scorecard was loaded and included in the agent context.")

    return {
        "cv_score": cv_score,
        "decision": decision,
        "reasons": reasons,
        "gap_analysis": gap_analysis,
        "candidate_profile": {
            "skills": cv_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "years_experience": years_experience,
        },
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "semantic_score": semantic_score,
    }
