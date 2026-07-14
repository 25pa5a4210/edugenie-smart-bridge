from datetime import datetime

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.history import LearningActivity
from app.models.user import User

router = APIRouter(prefix="/api/history", tags=["Learning History"])

VALID_TYPES = ["question", "concept", "quiz", "summary", "learning_path"]


class HistoryItem(BaseModel):
    id: int
    activity_type: str
    topic: str | None
    reference_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[HistoryItem], summary="Get learning history, optionally filtered by type")
def get_history(
    activity_type: str | None = Query(default=None, description="Filter by activity type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(LearningActivity).filter(LearningActivity.user_id == current_user.id)
    if activity_type:
        if activity_type not in VALID_TYPES:
            raise HTTPException(status_code=422, detail=f"activity_type must be one of {VALID_TYPES}")
        query = query.filter(LearningActivity.activity_type == activity_type)
    records = query.order_by(LearningActivity.created_at.desc()).limit(200).all()
    return [HistoryItem.model_validate(r) for r in records]


@router.delete("/{activity_id}", status_code=204, summary="Delete a history record")
def delete_history_item(activity_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(LearningActivity).filter(
        LearningActivity.id == activity_id, LearningActivity.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="History record not found.")
    db.delete(record)
    db.commit()
