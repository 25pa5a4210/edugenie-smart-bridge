from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=255)
    subject: Optional[str] = ""
    difficulty: str  # Easy | Medium | Hard
    num_questions: int = Field(ge=1, le=20)
    quiz_type: str  # "Multiple Choice Questions" | "True or False" | "Mixed Quiz"


class QuizQuestionOut(BaseModel):
    id: int
    question_text: str
    options: List[str]
    order_index: int

    model_config = {"from_attributes": True}


class QuizOut(BaseModel):
    id: int
    topic: str
    subject: Optional[str]
    difficulty: str
    quiz_type: str
    num_questions: int
    questions: List[QuizQuestionOut]
    created_at: datetime


class QuizSubmitAnswer(BaseModel):
    question_id: int
    selected_answer: str


class QuizSubmitRequest(BaseModel):
    quiz_id: int
    answers: List[QuizSubmitAnswer]


class AnswerResult(BaseModel):
    question_id: int
    question_text: str
    selected_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: str


class QuizResultResponse(BaseModel):
    attempt_id: int
    score: int
    total_questions: int
    percentage: float
    results: List[AnswerResult]
