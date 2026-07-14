from sqlalchemy.orm import Session

from app.models.quiz import Quiz, QuizAttempt
from app.models.history import LearningActivity
from app.models.user import User
from app.prompts.educational_prompts import recommendation_prompt
from app.services.gemini_service import gemini_service


def build_recommendations(db: Session, user: User) -> dict:
    # Recent topics from activity log
    recent_activity = (
        db.query(LearningActivity)
        .filter(LearningActivity.user_id == user.id)
        .order_by(LearningActivity.created_at.desc())
        .limit(10)
        .all()
    )
    recent_topics = list({a.topic for a in recent_activity if a.topic})[:8]

    # Weak topics = quizzes where attempt percentage < 60
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc())
        .limit(20)
        .all()
    )
    weak_topics = []
    total_pct = 0.0
    for attempt in attempts:
        total_pct += attempt.percentage
        if attempt.percentage < 60:
            quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
            if quiz:
                weak_topics.append(quiz.topic)

    avg_score = round(total_pct / len(attempts), 1) if attempts else 0.0

    prompt = recommendation_prompt(
        academic_level=user.academic_level,
        weak_topics=list(set(weak_topics))[:5],
        recent_topics=recent_topics,
        avg_quiz_score=avg_score,
    )
    data = gemini_service.generate_json(prompt)
    return {
        "topics_to_revise": data.get("topics_to_revise", []),
        "topics_to_learn_next": data.get("topics_to_learn_next", []),
        "weak_areas": data.get("weak_areas", []),
        "practice_suggestions": data.get("practice_suggestions", []),
        "disclaimer": "These are AI-generated suggestions based on your activity, not guaranteed academic outcomes.",
    }
