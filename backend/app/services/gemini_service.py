"""
Centralized Gemini AI service.

This is the ONLY place in the codebase that talks to the Gemini API.
All routers/services call methods on `gemini_service` instead of configuring
their own client. This keeps API-key handling, error handling, and JSON
parsing consistent across every AI feature.

Uses the official `google-genai` SDK (the current, non-deprecated client).
"""
import json
import logging
import re
from typing import Any, Optional

from google import genai
from google.genai import errors as genai_errors

from app.core.config import settings

logger = logging.getLogger("edugenie.gemini")


class GeminiServiceError(Exception):
    """Raised when the Gemini API call or response parsing fails."""


class GeminiService:
    def __init__(self):
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        if not settings.GEMINI_API_KEY:
            raise GeminiServiceError(
                "GEMINI_API_KEY is not configured. Set it in your .env file."
            )
        if self._client is None:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    def generate_text(self, prompt: str, temperature: float = 0.6) -> str:
        """Send a plain-text prompt to Gemini and return the raw text response."""
        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={"temperature": temperature},
            )
        except genai_errors.APIError as e:
            logger.error("Gemini API error: %s", e)
            raise GeminiServiceError(
                "The AI service is temporarily unavailable. Please try again shortly."
            ) from e
        except Exception as e:  # network errors, etc.
            logger.error("Unexpected Gemini error: %s", e)
            raise GeminiServiceError("An unexpected error occurred while contacting the AI service.") from e

        text = getattr(response, "text", None)
        if not text:
            raise GeminiServiceError("The AI service returned an empty response. Please try again.")
        return text.strip()

    def generate_json(self, prompt: str, temperature: float = 0.4) -> dict[str, Any]:
        """
        Send a prompt that instructs Gemini to return ONLY JSON, then safely
        parse and validate that JSON. Raises GeminiServiceError on any failure
        so routers can turn it into a clean HTTP error instead of crashing.
        """
        raw_text = self.generate_text(prompt, temperature=temperature)
        cleaned = self._strip_json_fences(raw_text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Attempt a best-effort recovery: extract the first {...} block
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                logger.error("Gemini returned non-JSON content: %s", raw_text[:500])
                raise GeminiServiceError(
                    "The AI returned an unexpected response format. Please try again."
                )
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError as e:
                logger.error("Failed to recover JSON from Gemini output: %s", raw_text[:500])
                raise GeminiServiceError(
                    "The AI returned an unexpected response format. Please try again."
                ) from e

        if not isinstance(data, dict):
            raise GeminiServiceError("The AI returned data in an unexpected shape. Please try again.")

        return data

    @staticmethod
    def _strip_json_fences(text: str) -> str:
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()


# Singleton instance used across the app
gemini_service = GeminiService()
