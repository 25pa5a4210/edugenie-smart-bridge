from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.concept import ConceptExplanation
from app.models.learning_path import LearningPath
from app.models.quiz import QuizAttempt
from app.models.conversation import AIMessage, AIConversation
from app.models.user import User, UserPreference
from app.schemas.auth import ACADEMIC_LEVELS, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users & Profile"])


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    academic_level: str | None = None


class PreferencesUpdateRequest(BaseModel):
    theme: str | None = None
    preferred_explanation_style: str | None = None
    quiz_difficulty_preference: str | None = None


class PreferencesResponse(BaseModel):
    theme: str
    preferred_explanation_style: str
    quiz_difficulty_preference: str

    model_config = {"from_attributes": True}


class ProfileStatsResponse(BaseModel):
    total_questions_asked: int
    quizzes_completed: int
    average_quiz_score: float
    learning_paths_created: int


@router.put("/me", response_model=UserResponse, summary="Update profile (name / academic level)")
def update_profile(payload: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.full_name:
        current_user.full_name = payload.full_name.strip()
    if payload.academic_level:
        if payload.academic_level not in ACADEMIC_LEVELS:
            raise HTTPException(status_code=422, detail=f"academic_level must be one of {ACADEMIC_LEVELS}")
        current_user.academic_level = payload.academic_level
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get("/me/preferences", response_model=PreferencesResponse, summary="Get user settings/preferences")
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return PreferencesResponse.model_validate(prefs)


@router.put("/me/preferences", response_model=PreferencesResponse, summary="Update user settings/preferences")
def update_preferences(payload: PreferencesUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)

    if payload.theme is not None:
        prefs.theme = payload.theme
    if payload.preferred_explanation_style is not None:
        prefs.preferred_explanation_style = payload.preferred_explanation_style
    if payload.quiz_difficulty_preference is not None:
        prefs.quiz_difficulty_preference = payload.quiz_difficulty_preference

    db.commit()
    db.refresh(prefs)
    return PreferencesResponse.model_validate(prefs)


@router.get("/me/stats", response_model=ProfileStatsResponse, summary="Get profile statistics")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_questions = (
        db.query(AIMessage)
        .join(AIConversation, AIMessage.conversation_id == AIConversation.id)
        .filter(AIConversation.user_id == current_user.id, AIMessage.role == "user")
        .count()
    )
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).all()
    avg_score = round(sum(a.percentage for a in attempts) / len(attempts), 1) if attempts else 0.0
    paths_count = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).count()

    return ProfileStatsResponse(
        total_questions_asked=total_questions,
        quizzes_completed=len(attempts),
        average_quiz_score=avg_score,
        learning_paths_created=paths_count,
    )
