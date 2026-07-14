from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.history import LearningActivity
from app.models.quiz import Quiz, QuizAnswer, QuizAttempt, QuizQuestion
from app.models.user import User
from app.prompts.educational_prompts import quiz_generation_prompt
from app.schemas.quiz import (
    AnswerResult,
    QuizGenerateRequest,
    QuizOut,
    QuizQuestionOut,
    QuizResultResponse,
    QuizSubmitRequest,
)
from app.services.gemini_service import GeminiServiceError, gemini_service
from app.services.quiz_service import options_from_json, options_to_json, validate_quiz_payload

router = APIRouter(prefix="/api/quizzes", tags=["Quiz Generator"])

VALID_DIFFICULTIES = ["Easy", "Medium", "Hard"]
VALID_TYPES = ["Multiple Choice Questions", "True or False", "Mixed Quiz"]


@router.post("/generate", response_model=QuizOut, summary="Generate a new AI quiz")
def generate_quiz(payload: QuizGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(status_code=422, detail=f"difficulty must be one of {VALID_DIFFICULTIES}")
    if payload.quiz_type not in VALID_TYPES:
        raise HTTPException(status_code=422, detail=f"quiz_type must be one of {VALID_TYPES}")

    prompt = quiz_generation_prompt(payload.topic, payload.subject or "", payload.difficulty, payload.num_questions, payload.quiz_type)

    try:
        data = gemini_service.generate_json(prompt)
        validated_questions = validate_quiz_payload(data, payload.num_questions)
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    quiz = Quiz(
        user_id=current_user.id,
        topic=payload.topic,
        subject=payload.subject,
        difficulty=payload.difficulty,
        quiz_type=payload.quiz_type,
        num_questions=len(validated_questions),
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for idx, q in enumerate(validated_questions):
        db.add(QuizQuestion(
            quiz_id=quiz.id,
            question_text=q["question_text"],
            options_json=options_to_json(q["options"]),
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
            order_index=idx,
        ))
    db.add(LearningActivity(user_id=current_user.id, activity_type="quiz", topic=payload.topic, reference_id=quiz.id))
    db.commit()
    db.refresh(quiz)

    return _quiz_to_out(quiz)


@router.get("/{quiz_id}", response_model=QuizOut, summary="Get a quiz by id")
def get_quiz(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return _quiz_to_out(quiz)


@router.post("/submit", response_model=QuizResultResponse, summary="Submit quiz answers and get scored results")
def submit_quiz(payload: QuizSubmitRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    questions = {q.id: q for q in quiz.questions}
    answers_map = {a.question_id: a.selected_answer for a in payload.answers}

    attempt = QuizAttempt(quiz_id=quiz.id, user_id=current_user.id, total_questions=len(questions))
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    score = 0
    results = []
    for q_id, question in questions.items():
        selected = answers_map.get(q_id)
        is_correct = bool(selected and selected.strip().lower() == question.correct_answer.strip().lower())
        if is_correct:
            score += 1
        db.add(QuizAnswer(
            attempt_id=attempt.id, question_id=q_id, selected_answer=selected, is_correct=1 if is_correct else 0,
        ))
        results.append(AnswerResult(
            question_id=q_id, question_text=question.question_text, selected_answer=selected,
            correct_answer=question.correct_answer, is_correct=is_correct, explanation=question.explanation or "",
        ))

    percentage = round((score / len(questions)) * 100, 1) if questions else 0.0
    attempt.score = score
    attempt.percentage = percentage
    db.commit()

    results.sort(key=lambda r: questions[r.question_id].order_index)

    return QuizResultResponse(
        attempt_id=attempt.id, score=score, total_questions=len(questions), percentage=percentage, results=results,
    )


def _quiz_to_out(quiz: Quiz) -> QuizOut:
    ordered_questions = sorted(quiz.questions, key=lambda q: q.order_index)
    return QuizOut(
        id=quiz.id, topic=quiz.topic, subject=quiz.subject, difficulty=quiz.difficulty,
        quiz_type=quiz.quiz_type, num_questions=quiz.num_questions,
        questions=[
            QuizQuestionOut(id=q.id, question_text=q.question_text, options=options_from_json(q.options_json), order_index=q.order_index)
            for q in ordered_questions
        ],
        created_at=quiz.created_at,
    )
