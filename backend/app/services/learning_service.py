from typing import Any

from app.services.gemini_service import GeminiServiceError


def validate_learning_path_payload(data: dict[str, Any]) -> list[dict]:
    phases = data.get("phases")
    if not isinstance(phases, list) or len(phases) == 0:
        raise GeminiServiceError("The AI did not return a valid learning roadmap. Please try again.")

    validated = []
    for phase in phases:
        title = phase.get("title")
        topics = phase.get("topics")
        if not title or not isinstance(topics, list) or len(topics) == 0:
            continue
        validated.append({
            "title": title,
            "topics": topics,
            "objectives": phase.get("objectives", ""),
            "recommended_practice": phase.get("recommended_practice", ""),
            "estimated_duration": phase.get("estimated_duration", ""),
            "mini_task": phase.get("mini_task", ""),
        })

    if not validated:
        raise GeminiServiceError("The AI response could not be validated into a usable roadmap. Please try again.")

    return validated
