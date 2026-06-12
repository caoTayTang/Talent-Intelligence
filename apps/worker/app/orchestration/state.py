from typing import Literal, TypedDict


class CVScreeningState(TypedDict):
    application_id: str
    job_id: str | None
    cv_object_key: str | None
    jd_text: str
    scorecard_json: dict | None

    raw_cv_text: str | None
    cv_text: str | None
    cv_profile: dict | None
    jd_rubric: dict | None
    cv_chunks: list[dict]
    jd_chunks: list[dict]
    cv_embeddings: list[list[float]]
    jd_embeddings: list[list[float]]
    retrieved_evidence: list[dict]
    evidence: list[dict]
    candidate_targets: list[dict]
    candidate_evidence: list[dict]
    external_evidence: list[dict]
    review_notes: list[str]
    risk_flags: list[str]
    react_steps: list[dict]
    criterion_scores: list[dict]

    candidate_profile: dict | None
    cv_score: float | None
    decision: Literal["pass", "fail"] | None
    decision_band: Literal["strong_pass", "pass", "review", "fail"] | None
    reasons: list[str]
    gap_analysis: str | None

    tool_trace: list[dict]
    errors: list[str]

class TestGeneratorState(TypedDict):
    application_id: str
    job_id: str | None
    jd_text: str
    cv_profile: dict | None
    test_config: dict | None
    test_content: dict | None
    errors: list[str]

    generation_retries: int
    validation_retries: int
    is_valid: bool