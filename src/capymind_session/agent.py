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
        # Prefer the "-latest" aliases; some environments/models require them.
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
        self._maybe_configure_gemini()

    def _maybe_configure_gemini(self) -> None:
        if genai is None:
            return
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)

    def _list_supported_models(self) -> List[str]:
        if genai is None:
            return []
        try:
            models = list(genai.list_models())
        except Exception:
            return []
        supported: List[str] = []
        for m in models:
            # google-generativeai exposes supported methods as supported_generation_methods
            methods = getattr(m, "supported_generation_methods", [])
            # Prefer chat/text generation-capable models
            if "generateContent" in methods or "generate_content" in methods:
                supported.append(getattr(m, "name", ""))
        return [name for name in supported if name]

    def _try_model_candidates(self) -> List[str]:
        # Ordered candidates to try when the chosen model fails
        candidates = [
            self.model,
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
        ]
        # Append any discoverable supported models not already included
        discovered = self._list_supported_models()
        for name in discovered:
            if name not in candidates:
                candidates.append(name)
        # Some APIs return fully qualified names like "models/gemini-1.5-flash"
        # Normalize by adding both raw and fully-qualified forms to try.
        normalized: List[str] = []
        for name in candidates:
            normalized.append(name)
            if not name.startswith("models/"):
                normalized.append(f"models/{name}")
        # Keep order and uniqueness
        seen = set()
        ordered_unique: List[str] = []
        for name in normalized:
            if name not in seen:
                seen.add(name)
                ordered_unique.append(name)
        return ordered_unique

    def _gemini_reply(self, messages: List[Dict[str, str]]) -> str:
        if genai is None or not os.getenv("GEMINI_API_KEY"):
            return (
                "Gemini is not configured. Please set GEMINI_API_KEY or install ADK support."
            )
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

        prompt = "\n".join(content_parts)

        last_error: Optional[Exception] = None
        for candidate in self._try_model_candidates():
            try:
                model = genai.GenerativeModel(candidate)
                response = model.generate_content(prompt)
                if getattr(response, "text", None):
                    # Update chosen model for subsequent turns
                    self.model = candidate if not candidate.startswith("models/") else candidate.split("/", 1)[-1]
                    return response.text
                # If no text, keep trying
            except Exception as e:  # NotFound / Unsupported / etc.
                last_error = e
                continue

        # If all candidates failed, report a helpful message
        hint_models = ", ".join(self._list_supported_models()[:6]) or "(no models discovered)"
        error_text = (
            "Gemini model not found or unsupported. "
            f"Tried candidates including '{self.model}'. "
            "You can set GEMINI_MODEL to a supported value (e.g., 'gemini-1.5-pro-latest').\n"
            f"Discovered models supporting generateContent: {hint_models}"
        )
        if last_error:
            error_text += f"\nLast error: {last_error}"
        return error_text

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
