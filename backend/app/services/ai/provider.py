"""
AI provider abstraction layer.
Supports OpenAI-compatible APIs via httpx.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(120.0, connect=10.0)


class AIProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_text(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2000) -> str:
        """Generate a plain-text response."""

    @abstractmethod
    async def generate_structured_output(self, prompt: str, schema: dict, system: Optional[str] = None) -> dict:
        """
        Generate a JSON response that conforms to *schema*.
        Raises ValueError if the model returns malformed JSON or schema violations.
        """


class OpenAIProvider(AIProvider):
    """OpenAI-compatible provider (works with OpenAI, Azure OpenAI, Groq, etc.)."""

    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def generate_text(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2000) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        logger.debug("AI text generated (%d chars)", len(content))
        return content.strip()

    async def generate_structured_output(
        self, prompt: str, schema: dict, system: Optional[str] = None
    ) -> dict:
        """
        Request JSON output from the model, with retry on parse failure.
        Uses response_format=json_object when possible.
        """
        sys_msg = (system or "") + (
            "\n\nYou MUST respond with valid JSON only. "
            "Do not include markdown code fences or any text outside the JSON object."
        )
        messages = [
            {"role": "system", "content": sys_msg.strip()},
            {"role": "user", "content": prompt},
        ]
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        raw = data["choices"][0]["message"]["content"].strip()

        # Strip markdown fences if the model added them despite instructions
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0].strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("AI returned malformed JSON: %s\nRaw: %s", exc, raw[:500])
            raise ValueError(f"AI response was not valid JSON: {exc}") from exc


class MockAIProvider(AIProvider):
    """
    Fallback provider used when no API key is configured.
    Returns plausible-looking stub data for development without an API key.
    """

    async def generate_text(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2000) -> str:
        return (
            "This is a stub AI response (no API key configured). "
            "Configure AI_API_KEY in your .env file to enable real AI features."
        )

    async def generate_structured_output(self, prompt: str, schema: dict, system: Optional[str] = None) -> dict:
        # Return a minimal valid structure so the app doesn't crash
        if "units" in str(schema):
            return {
                "subject": "Sample Subject",
                "units": [
                    {
                        "id": "unit1",
                        "name": "Introduction",
                        "description": "Introductory concepts",
                        "sequence": 1,
                        "topics": [
                            {
                                "id": "unit1_topic1",
                                "name": "Overview",
                                "description": "High-level overview",
                                "duration_hours": 1.0,
                                "objectives": ["Understand the basics"],
                            }
                        ],
                    }
                ],
                "warnings": ["Using stub AI provider – configure AI_API_KEY for real extraction"],
            }
        return {"result": "stub", "message": "Configure AI_API_KEY for real AI responses"}


def get_ai_provider() -> AIProvider:
    """Factory: return the configured AI provider instance."""
    if not settings.AI_API_KEY:
        logger.warning("AI_API_KEY not set – using MockAIProvider")
        return MockAIProvider()
    return OpenAIProvider(
        api_key=settings.AI_API_KEY,
        model=settings.AI_MODEL,
        base_url=settings.AI_BASE_URL,
    )
