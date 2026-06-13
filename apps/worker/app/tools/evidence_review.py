import json

from app.tools.llm import chat_json
from app.tools.web_search import tavily_search

MAX_REACT_STEPS = 3
MAX_TAVILY_SEARCHES = 2

SYSTEM_PROMPT = """
You are a bounded ReAct evidence reviewer for a recruiting CV screening system.
You review rubric scores and evidence quality. You may search only unresolved candidate targets provided in allowed_search_targets.
Never search generic skills, missing skills, tutorials, forums, or general technology definitions.
Never change cv_score or criterion_scores directly. Return JSON only.
""".strip()

ACTION_PROMPT = """
Choose the next action as JSON.
Allowed actions:
{"action":"tavily_search","target_id":"...","query":"...","reason":"..."}
{"action":"finish","review_notes":[...],"risk_flags":[...],"gap_analysis":"..."}
Limits: at most 2 Tavily searches, at most 3 total steps.
Prefer finish if unresolved targets are low value or existing evidence is enough.
""".strip()


def compact_text(text: str | None, max_chars: int = 1200) -> str:
    if not text:
        return ""
    return " ".join(text.split())[:max_chars]


def unresolved_targets(state: dict) -> list[dict]:
    targets = state.get("candidate_targets", [])
    evidence = state.get("candidate_evidence", [])
    verified_labels = {
        str(item.get("claim", "")).lower()
        for item in evidence
        if item.get("grade") == "verified"
    }
    unresolved = []
    for index, target in enumerate(targets, start=1):
        label = str(target.get("label") or "")
        if label and label.lower() not in " ".join(verified_labels):
            unresolved.append({"target_id": f"target_{index}", **target})
    return unresolved[:5]


def target_by_id(target_id: str, targets: list[dict]) -> dict | None:
    for target in targets:
        if target.get("target_id") == target_id:
            return target
    return None


def query_allowed(query: str, target: dict) -> bool:
    normalized = query.lower()
    label = str(target.get("label") or "").lower()
    query_hint = str(target.get("query") or "").lower()
    return bool(label and label in normalized) or bool(query_hint and query_hint in normalized)


def build_context(state: dict, external_evidence: list[dict], searches_used: int) -> tuple[dict, list[dict]]:
    targets = unresolved_targets(state)
    context = {
        "decision_band": state.get("decision_band"),
        "cv_score": state.get("cv_score"),
        "criterion_scores": state.get("criterion_scores", []),
        "evidence_summary": [
            {
                "id": item.get("id"),
                "grade": item.get("grade"),
                "source": item.get("source"),
                "claim": compact_text(item.get("claim"), 180),
                "confidence": item.get("confidence"),
                "notes": item.get("notes", []),
            }
            for item in state.get("evidence", [])[:20]
        ],
        "allowed_search_targets": targets,
        "external_evidence": external_evidence,
        "tavily_searches_used": searches_used,
    }
    return context, targets


def normalize_finish(payload: dict, external_evidence: list[dict], steps: list[dict], state: dict) -> dict:
    return {
        "review_notes": payload.get("review_notes", []),
        "risk_flags": payload.get("risk_flags", []),
        "gap_analysis": payload.get("gap_analysis") or state.get("gap_analysis") or "Evidence review completed.",
        "external_evidence": external_evidence,
        "react_steps": steps,
    }


def review_evidence_with_react(state: dict) -> dict:
    external_evidence: list[dict] = []
    steps: list[dict] = []
    searches_used = 0

    for step_index in range(1, MAX_REACT_STEPS + 1):
        context, targets = build_context(state, external_evidence, searches_used)
        if not targets:
            return normalize_finish(
                {
                    "review_notes": ["No unresolved candidate evidence targets remain."],
                    "risk_flags": [],
                    "gap_analysis": state.get("gap_analysis"),
                },
                external_evidence,
                steps + [{"step": step_index, "action": "finish_no_targets"}],
                state,
            )

        action = chat_json(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context JSON:\n{json.dumps(context)}\n\n{ACTION_PROMPT}"},
            ],
            temperature=0.0,
        )
        action_name = action.get("action")

        if action_name == "finish":
            steps.append({"step": step_index, "action": "finish"})
            return normalize_finish(action, external_evidence, steps, state)

        if action_name == "tavily_search" and searches_used < MAX_TAVILY_SEARCHES:
            target_id = str(action.get("target_id") or "")
            target = target_by_id(target_id, targets)
            query = str(action.get("query") or "").strip()
            if not target or not query or not query_allowed(query, target):
                steps.append(
                    {
                        "step": step_index,
                        "action": "blocked_search",
                        "target_id": target_id,
                        "query": query,
                        "reason": "query did not match an allowed unresolved candidate target",
                    }
                )
                return normalize_finish(action, external_evidence, steps, state)

            result = tavily_search(query=query, max_results=3)
            searches_used += 1
            external_evidence.append(
                {
                    "target_id": target_id,
                    "query": query,
                    "reason": action.get("reason"),
                    "answer": result.get("answer"),
                    "sources": result.get("sources", []),
                }
            )
            steps.append(
                {
                    "step": step_index,
                    "action": "tavily_search",
                    "target_id": target_id,
                    "sources": len(result.get("sources", [])),
                }
            )
            continue

        steps.append(
            {
                "step": step_index,
                "action": "finish_forced",
                "reason": f"unsupported or over-limit action: {action_name}",
            }
        )
        return normalize_finish(action, external_evidence, steps, state)

    return normalize_finish(
        {
            "review_notes": ["Reached ReAct step limit."],
            "risk_flags": [],
            "gap_analysis": state.get("gap_analysis"),
        },
        external_evidence,
        steps,
        state,
    )
