import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.concept import ConceptExplanation
from app.models.history import LearningActivity
from app.models.user import User
from app.prompts.educational_prompts import concept_explanation_prompt
from app.schemas.concept import ConceptRequest, ConceptResponse, ConceptResult
from app.services.gemini_service import GeminiServiceError, gemini_service

router = APIRouter(prefix="/api/concepts", tags=["Concept Explainer"])

VALID_STYLES = ["Simple", "Detailed", "Step-by-Step", "Real-Life Example", "Exam-Oriented"]


@router.post("/explain", response_model=ConceptResponse, summary="Get a structured AI explanation of a concept")
def explain_concept(payload: ConceptRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.style not in VALID_STYLES:
        raise HTTPException(status_code=422, detail=f"style must be one of {VALID_STYLES}")

    prompt = concept_explanation_prompt(payload.topic, payload.subject or "", payload.academic_level, payload.style)

    try:
        data = gemini_service.generate_json(prompt)
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    required_keys = ["definition", "explanation", "real_life_analogy", "important_points", "example", "quick_recap"]
    if not all(k in data for k in required_keys):
        raise HTTPException(status_code=502, detail="The AI response was missing required fields. Please try again.")

    result = ConceptResult(
        definition=data["definition"],
        explanation=data["explanation"],
        real_life_analogy=data["real_life_analogy"],
        important_points=data["important_points"] if isinstance(data["important_points"], list) else [str(data["important_points"])],
        example=data["example"],
        quick_recap=data["quick_recap"],
    )

    record = ConceptExplanation(
        user_id=current_user.id,
        topic=payload.topic,
        subject=payload.subject,
        academic_level=payload.academic_level,
        style=payload.style,
        result_json=json.dumps(result.model_dump()),
    )
    db.add(record)
    db.add(LearningActivity(user_id=current_user.id, activity_type="concept", topic=payload.topic, reference_id=None))
    db.commit()
    db.refresh(record)

    return ConceptResponse(
        id=record.id,
        topic=record.topic,
        subject=record.subject,
        academic_level=record.academic_level,
        style=record.style,
        result=result,
        created_at=record.created_at,
    )


@router.get("/history", response_model=list[ConceptResponse], summary="List past concept explanations")
def concept_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = (
        db.query(ConceptExplanation)
        .filter(ConceptExplanation.user_id == current_user.id)
        .order_by(ConceptExplanation.created_at.desc())
        .all()
    )
    out = []
    for r in records:
        result_data = json.loads(r.result_json)
        out.append(ConceptResponse(
            id=r.id, topic=r.topic, subject=r.subject, academic_level=r.academic_level,
            style=r.style, result=ConceptResult(**result_data), created_at=r.created_at,
        ))
    return out
