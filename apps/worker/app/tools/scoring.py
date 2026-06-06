# def score_cv_against_jd(cv_text: str, jd_text: str) -> dict:
#     """
#     Score CV fit against JD
#     TODO:
#     - extract skills
#     - embed CV/JD
#     - Compare semantic fit
#     - Call LLM for explaination
#     """
#     return {
#         "cv_score": 36.0,
#         "decision": "pass",
#         "reasons": [
#             "Mocked score for ae Thanh Hoa",
#             "Candidate nay de tem tot, approve!",
#         ],
#         "candidate_profile": {
#             "skills": ["Python", "FastAPI", "LLM"],
#             "years_experience": None,
#         },
#     }

### RULE BASED SCORING
import re


SKILL_KEYWORDS = {
    "python",
    "fastapi",
    "django",
    "sqlalchemy",
    "postgresql",
    "docker",
    "kubernetes",
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
}


def normalize(text: str) -> str:
    return text.lower()


def extract_skills(text: str) -> list[str]:
    normalized = normalize(text)
    found = []

    for skill in SKILL_KEYWORDS:
        if skill in normalized:
            found.append(skill)

    return sorted(found)


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


def score_cv_against_jd(cv_text: str, jd_text: str) -> dict:
    cv_skills = extract_skills(cv_text)
    jd_skills = extract_skills(jd_text)

    if not jd_skills:
        skill_score = 50.0
        matched_skills = []
        missing_skills = []
    else:
        matched_skills = sorted(set(cv_skills) & set(jd_skills))
        missing_skills = sorted(set(jd_skills) - set(cv_skills))
        skill_score = round((len(matched_skills) / len(jd_skills)) * 100, 2)

    years_experience = estimate_years_experience(cv_text)

    decision = "pass" if skill_score >= 60 else "fail"

    reasons = [
        f"Matched {len(matched_skills)} of {len(jd_skills)} required skill signals.",
        f"Matched skills: {', '.join(matched_skills) if matched_skills else 'none'}.",
        f"Missing skills: {', '.join(missing_skills) if missing_skills else 'none'}.",
    ]

    if years_experience is not None:
        reasons.append(
            f"Detected approximately {years_experience} years of experience."
        )

    return {
        "cv_score": skill_score,
        "decision": decision,
        "reasons": reasons,
        "candidate_profile": {
            "skills": cv_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "years_experience": years_experience,
        },
    }
