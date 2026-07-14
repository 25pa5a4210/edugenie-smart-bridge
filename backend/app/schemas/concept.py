from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ConceptRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=255)
    subject: Optional[str] = ""
    academic_level: str
    style: str  # Simple | Detailed | Step-by-Step | Real-Life Example | Exam-Oriented


class ConceptResult(BaseModel):
    definition: str
    explanation: str
    real_life_analogy: str
    important_points: List[str]
    example: str
    quick_recap: str


class ConceptResponse(BaseModel):
    id: int
    topic: str
    subject: Optional[str]
    academic_level: str
    style: str
    result: ConceptResult
    created_at: datetime
