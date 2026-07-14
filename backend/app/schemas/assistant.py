from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AskResponse(BaseModel):
    conversation_id: int
    answer: str
    messages: List[MessageResponse]


class ConversationSummary(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}
