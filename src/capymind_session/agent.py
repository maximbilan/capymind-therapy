from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .safety import check_crisis, crisis_response, safety_disclaimer

# Optional Gemini fallback
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    genai = None  # type: ignore

# Optional ADK (Google Agent Development Kit)
try:
    # Placeholder; concrete API surface may differ depending on ADK version
    import adk  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    adk = None  # type: ignore


SYSTEM_STYLE = (
    "You are a warm, validating, evidence-informed mental health support assistant. "
    "Use supportive, non-judgmental language. Encourage seeking professional help when needed. "
    "Avoid diagnosing or prescribing. Prefer brief, structured replies with optional exercises."
)

BOUNDARIES = (
    "Do not claim to be a licensed clinician. Do not provide crisis instructions beyond encouraging contacting emergency services and providing hotlines. "
    "If the user expresses intent or plan to harm self/others, immediately respond with crisis protocol."
)


class PocketTherapistAgent:
    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._maybe_configure_gemini()

    def _maybe_configure_gemini(self) -> None:
        if genai is None:
            return
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)

    def _gemini_reply(self, messages: List[Dict[str, str]]) -> str:
        if genai is None or not os.getenv("GEMINI_API_KEY"):
            return (
                "Gemini is not configured. Please set GEMINI_API_KEY or install ADK support."
            )
        model = genai.GenerativeModel(self.model)
        # Combine into a single prompt for simplicity in CLI usage
        content_parts: List[str] = [
            safety_disclaimer(),
            SYSTEM_STYLE,
            BOUNDARIES,
            "\nConversation so far:\n",
        ]
        for msg in messages:
            role = msg.get("role", "user")
            text = msg.get("content", "")
            content_parts.append(f"{role.upper()}: {text}")
        content_parts.append("\nASSISTANT:")
        response = model.generate_content("\n".join(content_parts))
        return response.text or "(no response)"

    def _adk_reply(self, messages: List[Dict[str, str]]) -> Optional[str]:
        if adk is None:
            return None
        try:
            # The specific API depends on ADK version; this is intentionally
            # isolated so failures gracefully fall back to Gemini.
            # Pseudocode-like usage:
            # agent = adk.create_agent(system=SYSTEM_STYLE + "\n" + BOUNDARIES)
            # return agent.chat(messages)
            return None
        except Exception:
            return None

    def reply(self, user_text: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        safety = check_crisis(user_text)
        if safety.level == "crisis":
            return crisis_response()

        messages: List[Dict[str, str]] = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        # Prefer ADK if available
        adk_text = self._adk_reply(messages)
        if adk_text:
            return adk_text

        return self._gemini_reply(messages)


def create_agent(model: Optional[str] = None) -> PocketTherapistAgent:
    return PocketTherapistAgent(model=model)
