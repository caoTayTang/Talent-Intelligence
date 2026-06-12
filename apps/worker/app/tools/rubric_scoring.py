SIGNAL_CONFIDENCE = {
    "claimed": 0.35,
    "retrieved": 0.65,
    "verified": 1.0,
    "unsupported": -0.15,
    "contradicted": -0.35,
}


def normalize(text: str | None) -> str:
    return (text or "").lower()


def signal_present(signal: str, text: str) -> bool:
    return normalize(signal) in normalize(text)


def evidence_text(evidence: dict) -> str:
    return " ".join(
        str(evidence.get(key) or "")
        for key in ["claim", "supporting_text", "url"]
    )


def score_criterion(criterion: dict, evidence: list[dict]) -> dict:
    signals = criterion.get("signals", [])
    matched_signals: list[str] = []
    missing_signals: list[str] = []
    evidence_ids: list[str] = []
    confidence_sum = 0.0

    for signal in signals:
        signal_matches = [item for item in evidence if signal_present(signal, evidence_text(item))]
        if signal_matches:
            matched_signals.append(signal)
            best = max(SIGNAL_CONFIDENCE.get(item.get("grade"), 0.0) for item in signal_matches)
            confidence_sum += max(0.0, best)
            evidence_ids.extend(item["id"] for item in signal_matches[:3])
        else:
            missing_signals.append(signal)

    if not signals:
        raw_score = 50.0
    else:
        raw_score = round((confidence_sum / len(signals)) * 100, 2)

    unsupported_hits = [
        item for item in evidence
        if item.get("grade") in {"unsupported", "contradicted"}
        and any(signal_present(signal, evidence_text(item)) for signal in signals)
    ]
    raw_score = max(0.0, raw_score - (len(unsupported_hits) * 5))
    weighted_score = round((raw_score / 100) * float(criterion.get("weight", 0)), 2)

    return {
        "criterion_id": criterion["id"],
        "label": criterion["label"],
        "weight": criterion["weight"],
        "raw_score": round(raw_score, 2),
        "weighted_score": weighted_score,
        "matched_signals": sorted(set(matched_signals)),
        "missing_signals": sorted(set(missing_signals)),
        "evidence_ids": sorted(set(evidence_ids)),
        "rationale": build_rationale(criterion, matched_signals, missing_signals, unsupported_hits),
    }


def build_rationale(
    criterion: dict,
    matched_signals: list[str],
    missing_signals: list[str],
    unsupported_hits: list[dict],
) -> str:
    parts = []
    if matched_signals:
        parts.append(f"Matched signals: {', '.join(sorted(set(matched_signals)))}.")
    if missing_signals:
        parts.append(f"Missing signals: {', '.join(sorted(set(missing_signals)))}.")
    if unsupported_hits:
        parts.append(f"Unsupported evidence count: {len(unsupported_hits)}.")
    return " ".join(parts) or f"No clear evidence for {criterion.get('label')}."


def decision_band(total_score: float) -> str:
    if total_score >= 85:
        return "strong_pass"
    if total_score >= 70:
        return "pass"
    if total_score >= 55:
        return "review"
    return "fail"


def score_rubric(jd_rubric: dict, evidence: list[dict]) -> dict:
    criterion_scores = [
        score_criterion(criterion, evidence)
        for criterion in jd_rubric.get("criteria", [])
    ]
    total_score = round(sum(item["weighted_score"] for item in criterion_scores), 2)
    band = decision_band(total_score)
    return {
        "cv_score": total_score,
        "decision_band": band,
        "decision": "fail" if band == "fail" else "pass",
        "criterion_scores": criterion_scores,
        "reasons": [
            f"{item['label']}: {item['raw_score']:.1f}/100 weighted={item['weighted_score']:.1f}"
            for item in criterion_scores
        ],
        "gap_analysis": build_gap_analysis(criterion_scores),
    }


def build_gap_analysis(criterion_scores: list[dict]) -> str:
    weakest = sorted(criterion_scores, key=lambda item: item["raw_score"])[:3]
    gaps = []
    for item in weakest:
        if item["missing_signals"]:
            gaps.append(f"{item['label']} missing {', '.join(item['missing_signals'][:4])}")
    return "; ".join(gaps) if gaps else "No major rubric gaps detected."
