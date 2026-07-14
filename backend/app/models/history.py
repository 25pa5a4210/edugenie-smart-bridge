from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class LearningActivity(Base):
    """A unified activity log used to power the History page and dashboard stats."""
    __tablename__ = "learning_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(30), nullable=False)  # question, concept, quiz, summary, learning_path
    topic = Column(String(255))
    reference_id = Column(Integer)  # id of related record (quiz id, concept id, etc.)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="activity_logs")
