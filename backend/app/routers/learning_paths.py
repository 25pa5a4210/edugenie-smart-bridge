from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.history import LearningActivity
from app.models.learning_path import LearningPath, LearningPhase, LearningTopic
from app.models.user import User
from app.prompts.educational_prompts import learning_path_prompt
from app.schemas.learning_path import (
    LearningPathOut,
    LearningPathRequest,
    PhaseOut,
    TopicCompleteRequest,
    TopicOut,
)
from app.services.gemini_service import GeminiServiceError, gemini_service
from app.services.learning_service import validate_learning_path_payload

router = APIRouter(prefix="/api/learning-paths", tags=["Learning Paths"])

VALID_LEVELS = ["Beginner", "Intermediate", "Advanced"]
VALID_GOALS = ["Academic Learning", "Exam Preparation", "Interview Preparation", "Project Development", "Career Skill"]


@router.post("/generate", response_model=LearningPathOut, summary="Generate a personalized learning roadmap")
def generate_learning_path(payload: LearningPathRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.knowledge_level not in VALID_LEVELS:
        raise HTTPException(status_code=422, detail=f"knowledge_level must be one of {VALID_LEVELS}")
    if payload.learning_goal not in VALID_GOALS:
        raise HTTPException(status_code=422, detail=f"learning_goal must be one of {VALID_GOALS}")

    prompt = learning_path_prompt(payload.topic, payload.knowledge_level, payload.learning_goal, payload.study_time)

    try:
        data = gemini_service.generate_json(prompt)
        validated_phases = validate_learning_path_payload(data)
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    path = LearningPath(
        user_id=current_user.id, topic=payload.topic, knowledge_level=payload.knowledge_level,
        learning_goal=payload.learning_goal, study_time=payload.study_time,
    )
    db.add(path)
    db.commit()
    db.refresh(path)

    for idx, phase_data in enumerate(validated_phases):
        phase = LearningPhase(
            path_id=path.id, title=phase_data["title"], objectives=phase_data["objectives"],
            recommended_practice=phase_data["recommended_practice"], estimated_duration=phase_data["estimated_duration"],
            mini_task=phase_data["mini_task"], order_index=idx,
        )
        db.add(phase)
        db.commit()
        db.refresh(phase)
        for topic_title in phase_data["topics"]:
            db.add(LearningTopic(phase_id=phase.id, title=topic_title, completed=False))
    db.add(LearningActivity(user_id=current_user.id, activity_type="learning_path", topic=payload.topic, reference_id=path.id))
    db.commit()
    db.refresh(path)

    return _path_to_out(path)


@router.get("", response_model=list[LearningPathOut], summary="List saved learning paths")
def list_learning_paths(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paths = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == current_user.id)
        .order_by(LearningPath.created_at.desc())
        .all()
    )
    return [_path_to_out(p) for p in paths]


@router.get("/{path_id}", response_model=LearningPathOut, summary="Get a single learning path")
def get_learning_path(path_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id, LearningPath.user_id == current_user.id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found.")
    return _path_to_out(path)


@router.put("/topics/{topic_id}/complete", response_model=TopicOut, summary="Mark a topic complete/incomplete")
def mark_topic_complete(topic_id: int, payload: TopicCompleteRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = (
        db.query(LearningTopic)
        .join(LearningPhase, LearningTopic.phase_id == LearningPhase.id)
        .join(LearningPath, LearningPhase.path_id == LearningPath.id)
        .filter(LearningTopic.id == topic_id, LearningPath.user_id == current_user.id)
        .first()
    )
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found.")
    topic.completed = payload.completed
    db.commit()
    db.refresh(topic)
    return TopicOut.model_validate(topic)


def _path_to_out(path: LearningPath) -> LearningPathOut:
    return LearningPathOut(
        id=path.id, topic=path.topic, knowledge_level=path.knowledge_level, learning_goal=path.learning_goal,
        study_time=path.study_time, progress_percentage=path.progress_percentage,
        phases=[
            PhaseOut(
                id=ph.id, title=ph.title, objectives=ph.objectives, recommended_practice=ph.recommended_practice,
                estimated_duration=ph.estimated_duration, mini_task=ph.mini_task,
                topics=[TopicOut.model_validate(t) for t in ph.topics],
            )
            for ph in path.phases
        ],
        created_at=path.created_at,
    )
