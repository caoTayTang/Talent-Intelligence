from langgraph.graph import END, StateGraph

from app.orchestration.state import CVScreeningState
from app.tools.db import (
    load_application_context,
    save_agent_run,
    update_cv_screening_result,
)

from app.tools.r2 import load_r2_text_object
from app.tools.scoring import score_cv_against_jd


def load_context(state: CVScreeningState) -> CVScreeningState:
    context = load_application_context(state["application_id"])

    return {
        **state,
        "job_id": context["job_id"],
        "cv_object_key": context["cv_object_key"],
        "jd_text": context["jd_text"],
    }


def load_cv_text(state: CVScreeningState) -> CVScreeningState:
    cv_object_key = state["cv_object_key"]
    if not cv_object_key:
        return {
            **state,
            "errors": state["errors"] + ["Application has no cv_object_key"],
        }

    cv_text = load_r2_text_object(cv_object_key)
    return {**state, "cv_text": cv_text}


def score_fit(state: CVScreeningState) -> CVScreeningState:
    if not state["cv_text"] or not state["jd_text"]:
        return {
            **state,
            "errors": state["errors"] + ["Missing CV or JD text."],
        }

    result = score_cv_against_jd(cv_text=state["cv_text"], jd_text=state["jd_text"])
    return {
        **state,
        "candidate_profile": result["candidate_profile"],
        "cv_score": result["cv_score"],
        "decision": result["decision"],
        "reasons": result["reasons"],
    }


def persist_result(state: CVScreeningState) -> CVScreeningState:
    output = {
        "job_id": state["job_id"],
        "cv_score": state["cv_score"],
        "decision": state["decision"],
        "reasons": state["reasons"],
        "candidate_profile": state["candidate_profile"],
        "errors": state["errors"],
    }

    save_agent_run(
        application_id=state["application_id"],
        agent_type="cv_screener",
        input_json={"application_id": state["application_id"]},
        output_json=output,
    )

    if state["cv_score"] is not None and state["decision"] is not None:
        update_cv_screening_result(
            application_id=state["application_id"],
            cv_score=state["cv_score"],
            decision=state["decision"],
            output=output,
        )

    return state


def build_cv_screening_graph():
    graph = StateGraph(CVScreeningState)
    graph.add_node("load_context", load_context)
    graph.add_node("load_cv_text", load_cv_text)
    graph.add_node("score_fit", score_fit)
    graph.add_node("persist_result", persist_result)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "load_cv_text")
    graph.add_edge("load_cv_text", "score_fit")
    graph.add_edge("score_fit", "persist_result")
    graph.add_edge("persist_result", END)
    return graph.compile()


cv_screening_graph = build_cv_screening_graph()


def run_cv_screening_graph(application_id: str) -> dict:
    initial_state: CVScreeningState = {
        "application_id": application_id,
        "job_id": None,
        "cv_object_key": None,
        "jd_text": "",
        "cv_text": None,
        "candidate_profile": None,
        "cv_score": None,
        "decision": None,
        "reasons": [],
        "errors": [],
    }

    return cv_screening_graph.invoke(initial_state)
