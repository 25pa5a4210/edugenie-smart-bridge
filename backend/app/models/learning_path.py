from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    knowledge_level = Column(String(30))
    learning_goal = Column(String(50))
    study_time = Column(String(30))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="learning_paths")
    phases = relationship("LearningPhase", back_populates="path", cascade="all, delete-orphan", order_by="LearningPhase.order_index")

    @property
    def progress_percentage(self) -> float:
        all_topics = [t for phase in self.phases for t in phase.topics]
        if not all_topics:
            return 0.0
        completed = sum(1 for t in all_topics if t.completed)
        return round((completed / len(all_topics)) * 100, 1)


class LearningPhase(Base):
    __tablename__ = "learning_phases"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    title = Column(String(255), nullable=False)
    objectives = Column(Text)
    recommended_practice = Column(Text)
    estimated_duration = Column(String(50))
    mini_task = Column(Text)
    order_index = Column(Integer, default=0)

    path = relationship("LearningPath", back_populates="phases")
    topics = relationship("LearningTopic", back_populates="phase", cascade="all, delete-orphan")


class LearningTopic(Base):
    __tablename__ = "learning_topics"

    id = Column(Integer, primary_key=True, index=True)
    phase_id = Column(Integer, ForeignKey("learning_phases.id"), nullable=False)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)

    phase = relationship("LearningPhase", back_populates="topics")
