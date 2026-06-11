import logging
from functools import wraps
from time import perf_counter
from uuid import UUID

from langgraph.graph import END, StateGraph

from talent_core.models import DocumentChunkSource, DocumentOwnerType

from app.orchestration.state import CVScreeningState
from app.tools.chunking import chunk_document
from app.tools.db import (
    load_application_context,
    save_agent_run,
    update_cv_screening_result,
)
from app.tools.embeddings import embed_texts
from app.tools.evidence import (
    claimed_evidence_from_profile,
    retrieved_evidence_from_matches,
    verify_candidate_targets,
)
from app.tools.evidence_review import review_evidence_with_react
from app.tools.profile_extraction import extract_cv_profile
from app.tools.r2 import load_r2_text_object
from app.tools.rubric import criterion_chunks, extract_jd_rubric
from app.tools.rubric_scoring import score_rubric
from app.tools.text_cleanup import clean_document_text
from app.tools.vector_store import replace_document_chunks, search_similar_chunks

logger = logging.getLogger(__name__)


def trace(
    state: CVScreeningState,
    tool: str,
    input_summary: str,
    output_summary: str,
    error: str | None = None,
) -> list[dict]:
    return state["tool_trace"] + [
        {
            "tool": tool,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "error": error,
        }
    ]


def logged_node(name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(state: CVScreeningState) -> CVScreeningState:
            started_at = perf_counter()
            logger.info(
                "cv_screening.%s.start application_id=%s job_id=%s errors=%d",
                name,
                state["application_id"],
                state.get("job_id"),
                len(state.get("errors", [])),
            )
            try:
                next_state = func(state)
            except Exception:
                logger.exception(
                    "cv_screening.%s.exception application_id=%s job_id=%s elapsed_ms=%.1f",
                    name,
                    state["application_id"],
                    state.get("job_id"),
                    (perf_counter() - started_at) * 1000,
                )
                raise

            latest_trace = (
                next_state.get("tool_trace", [])[-1]
                if next_state.get("tool_trace")
                else {}
            )
            logger.info(
                "cv_screening.%s.finish application_id=%s job_id=%s elapsed_ms=%.1f errors=%d output=%s error=%s",
                name,
                next_state["application_id"],
                next_state.get("job_id"),
                (perf_counter() - started_at) * 1000,
                len(next_state.get("errors", [])),
                latest_trace.get("output_summary"),
                latest_trace.get("error"),
            )
            return next_state

        return wrapper

    return decorator


@logged_node("load_context")
def load_context(state: CVScreeningState) -> CVScreeningState:
    context = load_application_context(state["application_id"])
    return {
        **state,
        "job_id": context["job_id"],
        "cv_object_key": context["cv_object_key"],
        "jd_text": context["jd_text"],
        "scorecard_json": context["scorecard_json"],
        "tool_trace": trace(
            state,
            "load_context",
            state["application_id"],
            f"loaded job_id={context['job_id']}",
        ),
    }


@logged_node("load_cv_text")
def load_cv_text(state: CVScreeningState) -> CVScreeningState:
    cv_object_key = state["cv_object_key"]
    if not cv_object_key:
        error = "Application has no cv_object_key"
        return {
            **state,
            "errors": state["errors"] + [error],
            "tool_trace": trace(state, "load_cv_text", "missing key", "skipped", error),
        }

    raw_cv_text = load_r2_text_object(cv_object_key)
    return {
        **state,
        "raw_cv_text": raw_cv_text,
        "tool_trace": trace(
            state,
            "load_cv_text",
            cv_object_key,
            f"loaded {len(raw_cv_text)} characters",
        ),
    }


@logged_node("clean_cv_text")
def clean_cv_text(state: CVScreeningState) -> CVScreeningState:
    cleaned = clean_document_text(state["raw_cv_text"] or "")
    return {
        **state,
        "cv_text": cleaned,
        "tool_trace": trace(
            state,
            "clean_cv_text",
            "raw_cv_text",
            f"cleaned {len(cleaned)} characters",
        ),
    }


@logged_node("extract_cv_profile")
def extract_profile(state: CVScreeningState) -> CVScreeningState:
    profile, error = extract_cv_profile(state["cv_text"] or "")
    errors = state["errors"] + ([f"CV profile fallback used: {error}"] if error else [])
    return {
        **state,
        "cv_profile": profile,
        "candidate_profile": profile,
        "errors": errors,
        "tool_trace": trace(
            state,
            "extract_cv_profile",
            "cv_text",
            f"projects={len(profile.get('projects', []))}, experience={len(profile.get('experience', []))}, source={profile.get('extraction_source')}",
            error,
        ),
    }


@logged_node("extract_jd_rubric")
def extract_rubric(state: CVScreeningState) -> CVScreeningState:
    jd_rubric = extract_jd_rubric(state["jd_text"], state["scorecard_json"])
    return {
        **state,
        "jd_rubric": jd_rubric,
        "tool_trace": trace(
            state,
            "extract_jd_rubric",
            "jd_text + scorecard_json",
            f"criteria={len(jd_rubric.get('criteria', []))}",
        ),
    }


@logged_node("chunk_documents")
def chunk_documents(state: CVScreeningState) -> CVScreeningState:
    cv_chunks = chunk_document(state["cv_text"] or "", source="cv")
    jd_chunks = criterion_chunks(state["jd_rubric"] or {})
    if not jd_chunks:
        jd_chunks = chunk_document(state["jd_text"], source="jd")

    errors = list(state["errors"])
    if not cv_chunks:
        errors.append("CV produced no chunks")
    if not jd_chunks:
        errors.append("JD produced no chunks")

    return {
        **state,
        "cv_chunks": cv_chunks,
        "jd_chunks": jd_chunks,
        "errors": errors,
        "tool_trace": trace(
            state,
            "chunk_documents",
            "cv_profile + jd_rubric",
            f"cv_chunks={len(cv_chunks)}, jd_chunks={len(jd_chunks)}",
        ),
    }


@logged_node("embed_and_index")
def embed_and_index(state: CVScreeningState) -> CVScreeningState:
    if not state["job_id"] or not state["cv_chunks"] or not state["jd_chunks"]:
        return {
            **state,
            "tool_trace": trace(
                state,
                "embed_and_index",
                "chunks",
                "skipped because required chunks/job_id are missing",
            ),
        }

    try:
        cv_embeddings = embed_texts(
            [chunk["text"] for chunk in state["cv_chunks"]], input_type="passage"
        )
        jd_embeddings = embed_texts(
            [chunk["text"] for chunk in state["jd_chunks"]], input_type="passage"
        )
        replace_document_chunks(
            owner_type=DocumentOwnerType.application,
            owner_id=UUID(state["application_id"]),
            source=DocumentChunkSource.cv,
            chunks=state["cv_chunks"],
            embeddings=cv_embeddings,
        )
        replace_document_chunks(
            owner_type=DocumentOwnerType.job,
            owner_id=UUID(state["job_id"]),
            source=DocumentChunkSource.jd,
            chunks=state["jd_chunks"],
            embeddings=jd_embeddings,
        )
        return {
            **state,
            "cv_embeddings": cv_embeddings,
            "jd_embeddings": jd_embeddings,
            "tool_trace": trace(
                state,
                "embed_and_index",
                "cv_chunks + jd_chunks",
                f"indexed {len(cv_embeddings)} CV and {len(jd_embeddings)} JD embeddings",
            ),
        }
    except Exception as exc:
        error = f"Embedding/indexing failed: {exc}"
        return {
            **state,
            "errors": state["errors"] + [error],
            "tool_trace": trace(state, "embed_and_index", "chunks", "failed", error),
        }


@logged_node("retrieve_rubric_evidence")
def retrieve_rubric_evidence(state: CVScreeningState) -> CVScreeningState:
    if not state["jd_embeddings"]:
        return {
            **state,
            "tool_trace": trace(
                state,
                "retrieve_rubric_evidence",
                "jd_embeddings",
                "skipped because embeddings are unavailable",
            ),
        }

    matches: list[dict] = []
    for jd_chunk, jd_embedding in zip(state["jd_chunks"], state["jd_embeddings"]):
        criterion_id = (jd_chunk.get("metadata") or {}).get("criterion_id")
        for match in search_similar_chunks(
            owner_type=DocumentOwnerType.application,
            owner_id=UUID(state["application_id"]),
            source=DocumentChunkSource.cv,
            query_embedding=jd_embedding,
            limit=3,
        ):
            matches.append(
                {
                    "criterion_id": criterion_id,
                    "jd_section": jd_chunk.get("section"),
                    "jd_text": jd_chunk.get("text"),
                    "cv_section": match["section"],
                    "cv_text": match["text"],
                    "similarity": match["similarity"],
                }
            )

    matches = sorted(matches, key=lambda item: item["similarity"], reverse=True)[:18]
    retrieved_evidence = retrieved_evidence_from_matches(matches)
    return {
        **state,
        "retrieved_evidence": matches,
        "evidence": state["evidence"] + retrieved_evidence,
        "tool_trace": trace(
            state,
            "retrieve_rubric_evidence",
            "rubric embeddings -> cv index",
            f"retrieved {len(matches)} rubric evidence matches",
        ),
    }


@logged_node("verify_public_evidence")
def verify_public_evidence(state: CVScreeningState) -> CVScreeningState:
    claimed = claimed_evidence_from_profile(state["cv_profile"] or {})
    try:
        targets, public_evidence = verify_candidate_targets(
            state["cv_text"] or "", state["cv_profile"] or {}, max_targets=6
        )
        return {
            **state,
            "candidate_targets": targets,
            "candidate_evidence": public_evidence,
            "evidence": state["evidence"] + claimed + public_evidence,
            "tool_trace": trace(
                state,
                "verify_public_evidence",
                "cv links, projects, companies",
                f"targets={len(targets)}, evidence={len(public_evidence)}",
            ),
        }
    except Exception as exc:
        error = f"Candidate evidence verification failed: {exc}"
        return {
            **state,
            "evidence": state["evidence"] + claimed,
            "errors": state["errors"] + [error],
            "tool_trace": trace(
                state,
                "verify_public_evidence",
                "cv links, projects, companies",
                "failed",
                error,
            ),
        }


@logged_node("score_rubric")
def score_by_rubric(state: CVScreeningState) -> CVScreeningState:
    result = score_rubric(state["jd_rubric"] or {}, state["evidence"])
    return {
        **state,
        "cv_score": result["cv_score"],
        "decision": result["decision"],
        "decision_band": result["decision_band"],
        "criterion_scores": result["criterion_scores"],
        "reasons": result["reasons"],
        "gap_analysis": result["gap_analysis"],
        "tool_trace": trace(
            state,
            "score_rubric",
            "jd_rubric + evidence",
            f"score={result['cv_score']}, band={result['decision_band']}",
        ),
    }


@logged_node("react_review_unresolved_evidence")
def react_review_unresolved_evidence(state: CVScreeningState) -> CVScreeningState:
    try:
        review = review_evidence_with_react(state)
        return {
            **state,
            "gap_analysis": review["gap_analysis"],
            "external_evidence": review["external_evidence"],
            "review_notes": review["review_notes"],
            "risk_flags": review["risk_flags"],
            "react_steps": review["react_steps"],
            "tool_trace": trace(
                state,
                "react_review_unresolved_evidence",
                "rubric score + evidence",
                f"react_steps={len(review['react_steps'])}, external_evidence={len(review['external_evidence'])}",
            ),
        }
    except Exception as exc:
        error = f"ReAct evidence review failed: {exc}"
        return {
            **state,
            "errors": state["errors"] + [error],
            "tool_trace": trace(
                state,
                "react_review_unresolved_evidence",
                "rubric score + evidence",
                "failed",
                error,
            ),
        }


@logged_node("persist_result")
def persist_result(state: CVScreeningState) -> CVScreeningState:
    output = {
        "agent": "cv_screener",
        "job_id": state["job_id"],
        "cv_score": state["cv_score"],
        "decision": state["decision"],
        "decision_band": state["decision_band"],
        "reasons": state["reasons"],
        "gap_analysis": state["gap_analysis"],
        "candidate_profile": state["candidate_profile"],
        "cv_profile": state["cv_profile"],
        "jd_rubric": state["jd_rubric"],
        "criterion_scores": state["criterion_scores"],
        "evidence": state["evidence"],
        "retrieved_evidence": state["retrieved_evidence"],
        "candidate_targets": state["candidate_targets"],
        "candidate_evidence": state["candidate_evidence"],
        "external_evidence": state["external_evidence"],
        "review_notes": state["review_notes"],
        "risk_flags": state["risk_flags"],
        "react_steps": state["react_steps"],
        "tool_trace": state["tool_trace"],
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

    return {
        **state,
        "tool_trace": trace(
            state,
            "persist_result",
            "agent_run + application",
            f"persisted={state['cv_score'] is not None}",
        ),
    }


def build_cv_screening_graph():
    graph = StateGraph(CVScreeningState)
    graph.add_node("load_context", load_context)
    graph.add_node("load_cv_text", load_cv_text)
    graph.add_node("clean_cv_text", clean_cv_text)
    graph.add_node("extract_cv_profile", extract_profile)
    graph.add_node("extract_jd_rubric", extract_rubric)
    graph.add_node("chunk_documents", chunk_documents)
    graph.add_node("embed_and_index", embed_and_index)
    graph.add_node("retrieve_rubric_evidence", retrieve_rubric_evidence)
    graph.add_node("verify_public_evidence", verify_public_evidence)
    graph.add_node("score_rubric", score_by_rubric)
    graph.add_node("react_review_unresolved_evidence", react_review_unresolved_evidence)
    graph.add_node("persist_result", persist_result)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "load_cv_text")
    graph.add_edge("load_cv_text", "clean_cv_text")
    graph.add_edge("clean_cv_text", "extract_cv_profile")
    graph.add_edge("extract_cv_profile", "extract_jd_rubric")
    graph.add_edge("extract_jd_rubric", "chunk_documents")
    graph.add_edge("chunk_documents", "embed_and_index")
    graph.add_edge("embed_and_index", "retrieve_rubric_evidence")
    graph.add_edge("retrieve_rubric_evidence", "verify_public_evidence")
    graph.add_edge("verify_public_evidence", "score_rubric")
    graph.add_edge("score_rubric", "react_review_unresolved_evidence")
    graph.add_edge("react_review_unresolved_evidence", "persist_result")
    graph.add_edge("persist_result", END)
    return graph.compile()


cv_screening_graph = build_cv_screening_graph()


def run_cv_screening_graph(application_id: str) -> dict:
    initial_state: CVScreeningState = {
        "application_id": application_id,
        "job_id": None,
        "cv_object_key": None,
        "jd_text": "",
        "scorecard_json": None,
        "raw_cv_text": None,
        "cv_text": None,
        "cv_profile": None,
        "jd_rubric": None,
        "cv_chunks": [],
        "jd_chunks": [],
        "cv_embeddings": [],
        "jd_embeddings": [],
        "retrieved_evidence": [],
        "evidence": [],
        "candidate_targets": [],
        "candidate_evidence": [],
        "external_evidence": [],
        "review_notes": [],
        "risk_flags": [],
        "react_steps": [],
        "criterion_scores": [],
        "candidate_profile": None,
        "cv_score": None,
        "decision": None,
        "decision_band": None,
        "reasons": [],
        "gap_analysis": None,
        "tool_trace": [],
        "errors": [],
    }
    return cv_screening_graph.invoke(initial_state)
