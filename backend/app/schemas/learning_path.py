from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LearningPathRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=255)
    knowledge_level: str  # Beginner | Intermediate | Advanced
    learning_goal: str  # Academic Learning | Exam Preparation | Interview Preparation | Project Development | Career Skill
    study_time: str  # 1 Week | 2 Weeks | 1 Month | 2 Months | custom string


class TopicOut(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = {"from_attributes": True}


class PhaseOut(BaseModel):
    id: int
    title: str
    objectives: Optional[str]
    recommended_practice: Optional[str]
    estimated_duration: Optional[str]
    mini_task: Optional[str]
    topics: List[TopicOut]

    model_config = {"from_attributes": True}


class LearningPathOut(BaseModel):
    id: int
    topic: str
    knowledge_level: str
    learning_goal: str
    study_time: str
    progress_percentage: float
    phases: List[PhaseOut]
    created_at: datetime


class TopicCompleteRequest(BaseModel):
    completed: bool
