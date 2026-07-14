import pytest

from app.services.gemini_service import GeminiServiceError
from app.services.learning_service import validate_learning_path_payload
from app.services.quiz_service import validate_quiz_payload


def test_validate_quiz_payload_accepts_well_formed_data():
    payload = {
        "questions": [
            {
                "question": "What is 2+2?",
                "options": ["1", "2", "3", "4"],
                "correct_answer": "4",
                "explanation": "Basic addition.",
            }
        ]
    }
    result = validate_quiz_payload(payload, expected_count=1)
    assert len(result) == 1
    assert result[0]["correct_answer"] == "4"


def test_validate_quiz_payload_rejects_empty_questions():
    with pytest.raises(GeminiServiceError):
        validate_quiz_payload({"questions": []}, expected_count=5)


def test_validate_quiz_payload_skips_malformed_question_but_keeps_valid_ones():
    payload = {
        "questions": [
            {"question": "Bad one", "options": ["only one"], "correct_answer": "x"},
            {
                "question": "Good one",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B",
                "explanation": "because",
            },
        ]
    }
    result = validate_quiz_payload(payload, expected_count=2)
    assert len(result) == 1
    assert result[0]["question_text"] == "Good one"


def test_validate_learning_path_payload_accepts_well_formed_data():
    payload = {
        "phases": [
            {
                "title": "Phase 1: Fundamentals",
                "topics": ["Basics", "Syntax"],
                "objectives": "Learn the basics",
                "recommended_practice": "Practice daily",
                "estimated_duration": "1 week",
                "mini_task": "Build a small script",
            }
        ]
    }
    result = validate_learning_path_payload(payload)
    assert len(result) == 1
    assert result[0]["title"] == "Phase 1: Fundamentals"


def test_validate_learning_path_payload_rejects_empty_phases():
    with pytest.raises(GeminiServiceError):
        validate_learning_path_payload({"phases": []})
