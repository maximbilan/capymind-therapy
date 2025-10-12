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
        self.model = model or os.getenv("CAPY_GEMINI_MODEL", "gemini-1.5-flash-latest")
        self._maybe_configure_gemini()

    def _maybe_configure_gemini(self) -> None:
        if genai is None:
            return
        api_key = os.getenv("CAPY_GEMINI_API_KEY")
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
        if genai is None or not os.getenv("CAPY_GEMINI_API_KEY"):
            return (
                "Gemini is not configured. Please set CAPY_GEMINI_API_KEY or install ADK support."
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
        # Try to import LlmAgent from likely locations
        LlmAgent = None  # type: ignore
        for path in ("adk.agents", "adk"):
            try:
                mod = __import__(path, fromlist=["LlmAgent"])  # type: ignore
                if hasattr(mod, "LlmAgent"):
                    LlmAgent = getattr(mod, "LlmAgent")
                    break
            except Exception:
                continue
        if LlmAgent is None:
            return None

        # Optional provider setup via envs
        provider = os.getenv("CAPY_ADK_PROVIDER", "ai_studio").lower()
        if provider == "vertex":
            try:
                import vertexai  # type: ignore
                project = os.getenv("CAPY_VERTEX_PROJECT")
                location = os.getenv("CAPY_VERTEX_LOCATION", "us-central1")
                if project:
                    vertexai.init(project=project, location=location)
            except Exception:
                # If Vertex init fails, fall back to AI Studio path
                provider = "ai_studio"

        if provider == "ai_studio":
            # Ensure downstream libraries see an API key, in case ADK expects a generic var
            api_key = os.getenv("CAPY_GEMINI_API_KEY")
            if api_key and not os.getenv("GEMINI_API_KEY"):
                os.environ["GEMINI_API_KEY"] = api_key

        # Prepare a single prompt string for broad compatibility
        transcript: List[str] = [
            safety_disclaimer(),
            SYSTEM_STYLE,
            BOUNDARIES,
            "",
            "Conversation so far:",
        ]
        for msg in messages:
            role = msg.get("role", "user").upper()
            text = msg.get("content", "")
            transcript.append(f"{role}: {text}")
        transcript.append("ASSISTANT:")
        prompt = "\n".join(transcript)

        try:
            agent = LlmAgent(system=SYSTEM_STYLE + "\n" + BOUNDARIES, model=self.model)  # type: ignore
        except Exception:
            # Fallback: try constructing without kwargs variations
            try:
                agent = LlmAgent(system=SYSTEM_STYLE + "\n" + BOUNDARIES)  # type: ignore
            except Exception:
                return None

        def _extract_text(resp: Any) -> Optional[str]:
            if resp is None:
                return None
            for attr in ("text", "output", "content"):
                if hasattr(resp, attr):
                    val = getattr(resp, attr)
                    if isinstance(val, str) and val.strip():
                        return val
            if isinstance(resp, dict):
                for key in ("text", "output", "content"):
                    val = resp.get(key)
                    if isinstance(val, str) and val.strip():
                        return val
            if isinstance(resp, str) and resp.strip():
                return resp
            return None

        # Try common method names with both messages and prompt
        attempts = [
            ("chat", messages),
            ("respond", messages),
            ("generate", prompt),
            ("run", prompt),
            ("invoke", prompt),
        ]
        for method_name, arg in attempts:
            try:
                method = getattr(agent, method_name, None)
                if callable(method):
                    resp = method(arg)  # type: ignore
                    text = _extract_text(resp)
                    if text:
                        return text
            except TypeError:
                # Retry with alternate arg shape (string vs list)
                try:
                    method = getattr(agent, method_name, None)
                    if callable(method):
                        alt_arg = prompt if isinstance(arg, list) else messages
                        resp = method(alt_arg)  # type: ignore
                        text = _extract_text(resp)
                        if text:
                            return text
                except Exception:
                    continue
            except Exception:
                continue

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
