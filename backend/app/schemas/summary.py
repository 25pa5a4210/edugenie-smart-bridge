from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    text: str = Field(min_length=20, max_length=20000)
    summary_type: str  # Short Summary | Detailed Notes | Key Points | Exam Revision Notes
    detail_level: str  # Brief | Standard | Detailed


class SummaryResult(BaseModel):
    main_summary: str
    key_concepts: List[str]
    important_points: List[str]
    important_terms: List[str]
    quick_revision: str


class SummaryResponse(BaseModel):
    id: int
    summary_type: str
    detail_level: str
    character_count: int
    result: SummaryResult
    created_at: datetime
