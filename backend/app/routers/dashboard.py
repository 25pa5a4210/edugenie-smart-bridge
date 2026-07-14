from datetime import datetime

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.history import LearningActivity
from app.models.learning_path import LearningPath
from app.models.quiz import QuizAttempt
from app.models.user import User
from app.services.recommendation_service import build_recommendations

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


class ActivityItem(BaseModel):
    id: int
    activity_type: str
    topic: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    questions_asked: int
    quizzes_taken: int
    average_quiz_score: float
    active_learning_paths: int


class DashboardResponse(BaseModel):
    welcome_name: str
    stats: DashboardStats
    recent_activity: list[ActivityItem]
    recommendations: dict


@router.get("", response_model=DashboardResponse, summary="Get aggregated dashboard data")
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    activity = (
        db.query(LearningActivity)
        .filter(LearningActivity.user_id == current_user.id)
        .order_by(LearningActivity.created_at.desc())
        .limit(8)
        .all()
    )
    questions_count = db.query(LearningActivity).filter(
        LearningActivity.user_id == current_user.id, LearningActivity.activity_type == "question"
    ).count()
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).all()
    avg_score = round(sum(a.percentage for a in attempts) / len(attempts), 1) if attempts else 0.0
    paths_count = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).count()

    try:
        recommendations = build_recommendations(db, current_user)
    except Exception:
        recommendations = {
            "topics_to_revise": [], "topics_to_learn_next": [], "weak_areas": [], "practice_suggestions": [],
            "disclaimer": "Recommendations will appear here once you start learning with EduGenie.",
        }

    return DashboardResponse(
        welcome_name=current_user.full_name,
        stats=DashboardStats(
            questions_asked=questions_count, quizzes_taken=len(attempts),
            average_quiz_score=avg_score, active_learning_paths=paths_count,
        ),
        recent_activity=[ActivityItem.model_validate(a) for a in activity],
        recommendations=recommendations,
    )
