from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.conversation import AIConversation, AIMessage
from app.models.history import LearningActivity
from app.models.user import User
from app.prompts.educational_prompts import question_answering_prompt
from app.schemas.assistant import AskRequest, AskResponse, ConversationSummary, MessageResponse
from app.services.gemini_service import GeminiServiceError, gemini_service

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])


@router.post("/ask", response_model=AskResponse, summary="Ask EduGenie an educational question")
def ask_question(payload: AskRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.conversation_id:
        conversation = (
            db.query(AIConversation)
            .filter(AIConversation.id == payload.conversation_id, AIConversation.user_id == current_user.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
    else:
        conversation = AIConversation(user_id=current_user.id, title=payload.question[:60])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    history_context = ""
    prior_messages = (
        db.query(AIMessage)
        .filter(AIMessage.conversation_id == conversation.id)
        .order_by(AIMessage.created_at.asc())
        .limit(10)
        .all()
    )
    if prior_messages:
        history_context = "\n".join(f"{m.role}: {m.content}" for m in prior_messages)

    user_message = AIMessage(conversation_id=conversation.id, role="user", content=payload.question)
    db.add(user_message)
    db.commit()

    prompt = question_answering_prompt(payload.question, current_user.academic_level, history_context)

    try:
        answer = gemini_service.generate_text(prompt)
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    ai_message = AIMessage(conversation_id=conversation.id, role="assistant", content=answer)
    db.add(ai_message)
    db.add(LearningActivity(user_id=current_user.id, activity_type="question", topic=payload.question[:255], reference_id=conversation.id))
    db.commit()

    messages = (
        db.query(AIMessage)
        .filter(AIMessage.conversation_id == conversation.id)
        .order_by(AIMessage.created_at.asc())
        .all()
    )

    return AskResponse(
        conversation_id=conversation.id,
        answer=answer,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.get("/conversations", response_model=list[ConversationSummary], summary="List past conversations")
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == current_user.id)
        .order_by(AIConversation.created_at.desc())
        .all()
    )
    return [ConversationSummary.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=list[MessageResponse], summary="Get messages for a conversation")
def get_conversation_messages(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = (
        db.query(AIConversation)
        .filter(AIConversation.id == conversation_id, AIConversation.user_id == current_user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = (
        db.query(AIMessage)
        .filter(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.created_at.asc())
        .all()
    )
    return [MessageResponse.model_validate(m) for m in messages]
