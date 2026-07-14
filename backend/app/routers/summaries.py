import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.history import LearningActivity
from app.models.summary import Summary
from app.models.user import User
from app.prompts.educational_prompts import summarization_prompt
from app.schemas.summary import SummaryRequest, SummaryResponse, SummaryResult
from app.services.gemini_service import GeminiServiceError, gemini_service

router = APIRouter(prefix="/api/summaries", tags=["Text Summarizer"])

VALID_TYPES = ["Short Summary", "Detailed Notes", "Key Points", "Exam Revision Notes"]
VALID_LEVELS = ["Brief", "Standard", "Detailed"]
MAX_CHARS = 20000


@router.post("/generate", response_model=SummaryResponse, summary="Summarize educational text with AI")
def generate_summary(payload: SummaryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.summary_type not in VALID_TYPES:
        raise HTTPException(status_code=422, detail=f"summary_type must be one of {VALID_TYPES}")
    if payload.detail_level not in VALID_LEVELS:
        raise HTTPException(status_code=422, detail=f"detail_level must be one of {VALID_LEVELS}")
    if len(payload.text.strip()) == 0:
        raise HTTPException(status_code=422, detail="Text cannot be empty.")
    if len(payload.text) > MAX_CHARS:
        raise HTTPException(status_code=422, detail=f"Text exceeds the maximum of {MAX_CHARS} characters.")

    prompt = summarization_prompt(payload.text, payload.summary_type, payload.detail_level)

    try:
        data = gemini_service.generate_json(prompt)
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    required_keys = ["main_summary", "key_concepts", "important_points", "important_terms", "quick_revision"]
    if not all(k in data for k in required_keys):
        raise HTTPException(status_code=502, detail="The AI response was missing required fields. Please try again.")

    result = SummaryResult(
        main_summary=data["main_summary"],
        key_concepts=data["key_concepts"] if isinstance(data["key_concepts"], list) else [],
        important_points=data["important_points"] if isinstance(data["important_points"], list) else [],
        important_terms=data["important_terms"] if isinstance(data["important_terms"], list) else [],
        quick_revision=data["quick_revision"],
    )

    record = Summary(
        user_id=current_user.id,
        original_text=payload.text,
        summary_type=payload.summary_type,
        detail_level=payload.detail_level,
        result_json=json.dumps(result.model_dump()),
    )
    db.add(record)
    db.add(LearningActivity(user_id=current_user.id, activity_type="summary", topic=payload.summary_type, reference_id=None))
    db.commit()
    db.refresh(record)

    return SummaryResponse(
        id=record.id, summary_type=record.summary_type, detail_level=record.detail_level,
        character_count=len(payload.text), result=result, created_at=record.created_at,
    )


@router.get("/history", response_model=list[SummaryResponse], summary="List past summaries")
def summary_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = (
        db.query(Summary)
        .filter(Summary.user_id == current_user.id)
        .order_by(Summary.created_at.desc())
        .all()
    )
    out = []
    for r in records:
        result_data = json.loads(r.result_json)
        out.append(SummaryResponse(
            id=r.id, summary_type=r.summary_type, detail_level=r.detail_level,
            character_count=len(r.original_text), result=SummaryResult(**result_data), created_at=r.created_at,
        ))
    return out
