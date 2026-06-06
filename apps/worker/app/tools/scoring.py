def score_cv_against_jd(cv_text: str, jd_text: str) -> dict:
    """
    Score CV fit against JD
    TODO:
    - extract skills
    - embed CV/JD
    - Compare semantic fit
    - Call LLM for explaination
    """
    return {
        "cv_score": 36.0,
        "decision": "pass",
        "reasons": [
            "Mocked score for ae Thanh Hoa",
            "Candidate nay de tem tot, approve!",
        ],
        "candidate_profile": {
            "skills": ["Python", "FastAPI", "LLM"],
            "years_experience": None,
        },
    }
