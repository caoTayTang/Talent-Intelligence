from pydantic import BaseModel, Field
from typing import List, Literal, Optional

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