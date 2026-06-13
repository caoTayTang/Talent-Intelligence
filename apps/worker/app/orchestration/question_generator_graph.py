import json
import logging
import time

from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from langgraph.graph import END, StateGraph
from app.orchestration.state import TestGeneratorState
from app.tools.db import load_application_context, update_dynamic_test_content
from app.tools.llm import chat_json
from app.tools.r2 import load_r2_text_object
from app.tools.profile_extraction import extract_cv_profile

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

class MCQOptions(BaseModel):
    label: str = Field(description="Choice symbol (VD: A, B, C, D)")
    text: str = Field(description="Choice content")

class Question(BaseModel):
    id: str = Field(description="Question ID")
    type: Literal["multiple_choice", "essay"]
    content: str = Field(description="Question content")
    points: int = Field(description="Points for the question")

    options: Optional[List[MCQOptions]] = Field(description="List of options for multiple choice questions - type = multiple_choice")

    expected_answer: Optional[str] = Field(description="Expected answer for questions")
    hints: Optional[List[str]] = Field(description="List of hints for the question")

class DynamicTestStructure(BaseModel):
    test_title: str = Field(description="Title of the test base on JD")
    time_limit_minutes: int = Field(description="Time limit for the test in minutes")
    questions: List[Question] = Field(description="List of questions in the test")


def load_context(state: TestGeneratorState) -> TestGeneratorState:
    logger.info(f"generator.load_context application_id={state['application_id']}")
    context = load_application_context(state["application_id"])

    cv_object_key = context["cv_object_key"]
    cv_profile = {}
    error = state["errors"]

    if cv_object_key:
        try:
            raw_cv_text = load_r2_text_object(cv_object_key)
            profile_data, ext_err = extract_cv_profile(raw_cv_text)
            cv_profile = profile_data
            if ext_err:
                error.append(f"Profile extraction warning: {ext_err}")
        
        except Exception as e:
            error.append(f"Failed to load or extract CV: {str(e)}")
    else:
        error.append("No cv_object_key found in application context.")
    
    return {
        **state,
        "job_id": context["job_id"],
        "jd_text": context["jd_text"] or "",
        "cv_profile": cv_profile,
        "test_config": context.get("dynamic_test_config"),
        "errors": error,
    }

def generate_questions(state: TestGeneratorState) -> TestGeneratorState:
    retries = state.get("generation_retries", 0)
    logger.info(f"generator.generate_questions application_id={state['application_id']}")

    # 1. Extract Pydantic Schema to JSON string
    schema_str = json.dumps(DynamicTestStructure.model_json_schema(), ensure_ascii=False, indent=2)
    
    # 2. Process HR's dynamic test config
    config = state.get("test_config")
    print(f"Test config: {config}")
    if config:
        rules_text = f"MANDATORY: Adhere to the following point budget (Total test points: {config.get('total_points', 100)}):\n"
        dist = config.get("distribution", {})
        
        if "multiple_choice" in dist and dist["multiple_choice"].get("count", 0) > 0:
            count = dist["multiple_choice"]["count"]
            pts = dist["multiple_choice"]["total_category_points"]
            rules_text += f"- Multiple Choice (multiple_choice): EXACTLY {count} questions, totaling {pts} points. You may distribute points equally among them.\n"
            
        if "essay" in dist and dist["essay"].get("count", 0) > 0:
            count = dist["essay"]["count"]
            pts = dist["essay"]["total_category_points"]
            rules_text += f"- Essay (essay): EXACTLY {count} questions, totaling {pts} points. You MUST allocate points (points field) for each essay question based on its difficulty, length, and domain importance. Niche/hard questions must be assigned higher points a little bit.\n"
            rules_text += "- 'requires_file_upload' flag: Set this to true ONLY for essay questions that strictly require the candidate to draw architectural diagrams (System Design), database schemas, or complex logic flowcharts.\n"
    else:
        rules_text = "Flexibly combine Multiple Choice and Essay questions. Allocate points for each question based on difficulty so the total equals the requested budget."

    # 3. Inject into System Prompt
    system_prompt = f"""You are a Senior Tech Lead. Your task is to create an in-depth competency test based on the company's Job Description (JD) and the candidate's CV.

    BUSINESS REQUIREMENTS:
    1. IDENTIFY SENIORITY & CALIBRATE DIFFICULTY: Analyze the JD and CV to determine the target seniority level (e.g., Intern, Fresher, Junior, Mid-level, Senior). You MUST calibrate the difficulty and depth of the questions accordingly:
    - For Intern/Fresher: Focus heavily on fundamental domain knowledge, basic theoretical concepts, algorithmic thinking, and academic/personal projects.
    - For Junior/Mid-level: Focus on practical application, framework-specific knowledge, standard problem-solving, and best practices.
    - For Senior/Lead: Focus heavily on system architecture, design patterns, trade-offs, scalability, and handling edge cases in production.

    2. QUESTION MIX: Ensure a balanced mix of questions:
    - Core Fundamentals: Questions testing theoretical and fundamental knowledge of the specific domain.
    - Deep-Dives: Questions deeply targeting specific technologies and projects claimed in the candidate's CV that match the JD.

    3. GRADING RUBRIC: Provide extremely detailed 'expected_answer' (grading rubrics or key points) for every question. The AI grading system will strictly use this to evaluate the candidate later.

    4. POINT DISTRIBUTION RULES:
    {rules_text}

    MANDATORY: RETURN ONLY A VALID JSON OBJECT EXACTLY MATCHING THE STRUCTURE BELOW. DO NOT WRAP THE JSON IN MARKDOWN BLOCKS (e.g., ```json).
    {schema_str}
    """

    user_prompt = f"COMPANY JD:\n{state['jd_text']}\n\nCANDIDATE CV PROFILE:\n{json.dumps(state['cv_profile'], ensure_ascii=False)}"

    try:
        # Call LLM
        response_dict = chat_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        # Pydantic Validation
        validated_data = DynamicTestStructure.model_validate(response_dict)
        return {**state, "test_content": validated_data.model_dump(), "generation_retries": retries + 1}
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Generation failed: {error_msg}")
        
        # NẾU BỊ GROQ CHẶN RATE LIMIT -> BẮT WORKER NGỦ 30 GIÂY RỒI MỚI CHẠY LẠI
        if "429" in error_msg or "Rate limit" in error_msg:
            logger.info("Rate limit hit. Sleeping for 20 seconds before retry...")
            time.sleep(30)
        return {**state, "errors": state["errors"] + [f"Gen Error: {str(e)}"], "generation_retries": retries + 1}
    
def validate_questions(state: TestGeneratorState) -> TestGeneratorState:
    """Principal Engineer đánh giá và tinh chỉnh lại đề thi."""
    retries = state.get("validation_retries", 0)
    logger.info(f"generator.validate_questions application_id={state['application_id']}")

    # Nếu bước sinh đề trước đó bị lỗi, bỏ qua bước này
    if not state.get("test_content"):
        return {**state, "validation_retries": retries + 1, "is_valid": False}

    schema_str = json.dumps(DynamicTestStructure.model_json_schema(), ensure_ascii=False, indent=2)
    
    # Lấy ngân sách điểm để Principal Engineer đối chiếu
    config = state.get("test_config")
    target_points = config.get("total_points", 100) if config else 100

    system_prompt = f"""You are a Principal Engineer reviewing a competency test created by a Tech Lead.
    Your job is to strictly VALIDATE and REFINE the provided test JSON based on the JD and CV.

    CHECKLIST FOR REFINEMENT:
    1. DIFFICULTY CHECK: Is the test too hard or too easy for the expected seniority level in the JD? If it's too academic for a Senior, change it to system design. If it's too complex for an Intern, simplify it to fundamentals.
    2. MATH CHECK: The sum of 'points' for all questions MUST EXACTLY EQUAL {target_points}. If it does not, adjust the points to match perfectly.
    3. QUALITY CHECK: Ensure 'expected_answer' is extremely detailed for the grading AI.

    If the test is already perfect, output it as is. If it needs adjustments, output the corrected version.
    MANDATORY: RETURN ONLY A VALID JSON OBJECT EXACTLY MATCHING THIS SCHEMA:
    {schema_str}
    """

    user_prompt = f"""COMPANY JD: {state['jd_text']}

    CANDIDATE CV PROFILE: {json.dumps(state['cv_profile'], ensure_ascii=False)}

    DRAFT TEST GENERATED BY TECH LEAD: {json.dumps(state['test_content'], ensure_ascii=False)}

    Please review, correct any point miscalculations, adjust difficulty if necessary, and output the FINAL JSON.
    """

    try:
        response_dict = chat_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2 
        )
        
        # Validate lại lần cuối với Pydantic
        validated_data = DynamicTestStructure.model_validate(response_dict)
        return {**state, "test_content": validated_data.model_dump(), "is_valid": True, "validation_retries": retries + 1}
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Validation failed: {error_msg}")
        
        # NẾU BỊ GROQ CHẶN RATE LIMIT -> BẮT WORKER NGỦ 20 GIÂY RỒI MỚI CHẠY LẠI
        if "429" in error_msg or "Rate limit" in error_msg:
            logger.info("Rate limit hit. Sleeping for 30 seconds before retry...")
            time.sleep(30)
        return {**state, "errors": state["errors"] + [f"Val Error: {str(e)}"], "validation_retries": retries + 1, "is_valid": False}


def persist_test(state: TestGeneratorState) -> TestGeneratorState:
    """Lưu đề thi xuống Database."""
    if state.get("test_content"):
        logger.info(f"generator.persist_test application_id={state['application_id']}")
        try:
            update_dynamic_test_content(
                application_id=state["application_id"], 
                test_content=state["test_content"]
            )
        except Exception as e:
            logger.error(f"Failed to persist test content: {e}")
            return {**state, "errors": state["errors"] + [f"DB Persist Error: {e}"]}
    return state

# Routeing functions to determine next step based on state
def route_after_generation(state: TestGeneratorState) -> str:
    """Quyết định đi đâu sau khi Gen đề xong."""
    if state.get("test_content"):
        return "validate_questions" 
    if state.get("generation_retries", 0) < MAX_RETRIES:
        return "generate_questions"  
    return "persist_test"            

def route_after_validation(state: TestGeneratorState) -> str:
    """Quyết định đi đâu sau khi Duyệt đề xong."""
    if state.get("is_valid"):
        return "persist_test"        
    if state.get("validation_retries", 0) < MAX_RETRIES:
        return "validate_questions"  
    return "persist_test"            

def build_generator_graph():
    """Ráp các Node lại thành Graph với luồng Actor-Critic."""
    graph = StateGraph(TestGeneratorState)
    
    # 1. Khai báo các Node
    graph.add_node("load_context", load_context)
    graph.add_node("generate_questions", generate_questions)
    graph.add_node("validate_questions", validate_questions) # THÊM NODE REVIEW
    graph.add_node("persist_test", persist_test)

    # 2. Vẽ đường đi (Edges)
    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "generate_questions")
    
    # conditional edge sau khi Gen đề xong
    graph.add_conditional_edges(
        "generate_questions",
        route_after_generation,
        {
            "validate_questions": "validate_questions",
            "generate_questions": "generate_questions",
            "persist_test": "persist_test"
        }
    )

    # conditional edge sau khi Duyệt đề xong
    graph.add_conditional_edges(
        "validate_questions",
        route_after_validation,
        {
            "persist_test": "persist_test",
            "validate_questions": "validate_questions"
        }
    )

    graph.add_edge("persist_test", END)
    
    return graph.compile()

# Khởi tạo instance của graph
generator_graph = build_generator_graph()

def run_generator_graph(application_id: str) -> dict:
    """Hàm wrapper để Celery Task gọi."""
    initial_state: TestGeneratorState = {
        "application_id": application_id,
        "job_id": None,
        "jd_text": "",
        "cv_profile": None,
        "test_config": None,
        "test_content": None,
        "errors": [],
        "generation_retries": 0,
        "validation_retries": 0,
        "is_valid": False
    }
    return generator_graph.invoke(initial_state)