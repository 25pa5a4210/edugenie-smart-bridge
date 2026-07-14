from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ConceptExplanation(Base):
    __tablename__ = "concept_explanations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    subject = Column(String(120))
    academic_level = Column(String(50))
    style = Column(String(30))
    result_json = Column(Text, nullable=False)  # structured explanation stored as JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="concept_explanations")
