import json
from typing import Any

from app.services.gemini_service import GeminiServiceError


def validate_quiz_payload(data: dict[str, Any], expected_count: int) -> list[dict]:
    """
    Validate the structure of Gemini's quiz JSON output. Raises GeminiServiceError
    with a user-safe message if anything is malformed, so callers never crash
    on unpredictable AI output.
    """
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) == 0:
        raise GeminiServiceError("The AI did not return valid quiz questions. Please try again.")

    validated = []
    for q in questions[:expected_count] if len(questions) > expected_count else questions:
        question_text = q.get("question")
        options = q.get("options")
        correct_answer = q.get("correct_answer")
        explanation = q.get("explanation", "")

        if not question_text or not isinstance(options, list) or len(options) < 2 or not correct_answer:
            continue  # skip malformed question rather than failing the whole quiz
        if correct_answer not in options:
            # try case-insensitive match, else skip
            match = next((o for o in options if o.strip().lower() == str(correct_answer).strip().lower()), None)
            if not match:
                continue
            correct_answer = match

        validated.append({
            "question_text": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation,
        })

    if not validated:
        raise GeminiServiceError("The AI response could not be validated into a usable quiz. Please try again.")

    return validated


def options_to_json(options: list[str]) -> str:
    return json.dumps(options)


def options_from_json(options_json: str) -> list[str]:
    return json.loads(options_json)
