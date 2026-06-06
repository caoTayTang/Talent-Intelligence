from typing import Literal, TypedDict


class CVScreeningState(TypedDict):
    application_id: str
    job_id: str | None
    cv_object_key: str | None
    cv_text: str | None
    jd_text: str

    candidate_profile: dict | None
    cv_score: float | None
    decision: Literal["pass", "fail"] | None
    reasons: list[str]
    errors: list[str]
