import json
import os
import logging
from typing import Dict, Any, List

import requests
from google.cloud import firestore
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token as google_id_token


def _firestore_client():
    return firestore.Client(project=os.getenv("CAPY_PROJECT_ID"))


def _get_last_notes(user_id: str, limit: int = 5) -> List[str]:
    db = _firestore_client()
    user_ref = db.collection("users").document(user_id)
    notes = (
        db.collection("notes")
        .where("user", "==", user_ref)
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    texts: List[str] = []
    for doc in notes:
        data = doc.to_dict() or {}
        text = data.get("text", "")
        if text:
            texts.append(text)
    return texts


def _build_prompt(user_message: str, last_notes: List[str], language_name: str) -> str:
    history = "\n\n".join(f"- {n}" for n in last_notes) if last_notes else "(no prior notes)"
    return (
        "You are a supportive, empathetic therapist. Use the user's prior journal "
        "notes to personalize guidance. Keep responses concise, kind, and practical.\n"
        f"Always reply in {language_name}.\n\n"
        f"User message: {user_message}\n\n"
        f"Recent notes:\n{history}"
    )


def _get_user_locale(user_id: str) -> str:
    db = _firestore_client()
    doc = db.collection("users").document(user_id).get()
    data = doc.to_dict() or {}
    locale = data.get("locale") or "en"
    if locale not in ("en", "uk"):
        locale = "en"
    return locale


def _gemini_reply(prompt: str) -> str:
    # Prefer GOOGLE_API_KEY (standard for Google AI SDK). Fallback to CAPY_GEMINI_API_KEY.
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("CAPY_GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY (or CAPY_GEMINI_API_KEY) is not set")
    try:
        import google.generativeai as genai  # lazy import
    except Exception as imp_err:
        raise RuntimeError(f"google-generativeai not available: {imp_err}")

    genai.configure(api_key=key)
    model_name = os.getenv("CAPY_GEMINI_MODEL", "gemini-1.5-flash-latest")
    model = genai.GenerativeModel(model_name)
    resp = model.generate_content(prompt)
    try:
        text = resp.text or ""
    except Exception:
        # Best-effort extract
        text = getattr(resp, "candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    if not text:
        text = "I'm here with you. Could you share more about how you're feeling?"
    return text


def _adk_api_reply(prompt: str, logger: logging.Logger, session_id: str | None = None) -> str:
    """Call the ADK agent over Cloud Run HTTP using ID token auth.

    Environment variables:
    - ADK_CLOUD_RUN_URL (preferred) or CAPY_ADK_URL: Full HTTPS URL to the ADK service root
    - ADK_TIMEOUT_SECS (optional): HTTP timeout in seconds (default: 60)
    """
    url = os.getenv("ADK_CLOUD_RUN_URL") or os.getenv("CAPY_ADK_URL")
    if not url:
        raise RuntimeError("ADK_CLOUD_RUN_URL (or CAPY_ADK_URL) is not set")

    timeout = float(os.getenv("ADK_TIMEOUT_SECS", "60"))

    # Acquire an ID token for the Cloud Run service audience (use the URL as audience)
    try:
        auth_req = GoogleAuthRequest()
        token = google_id_token.fetch_id_token(auth_req, url)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch ID token for audience {url}: {e}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Common ADK HTTP payload shape is {"input": "..."}; optionally include session_id
    payload: Dict[str, Any] = {"input": prompt}
    if session_id:
        # Many ADK runtimes accept session_id for per-user memory. Extra fields are ignored otherwise.
        payload["session_id"] = session_id

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"HTTP request to ADK service failed: {e}")

    if resp.status_code >= 400:
        raise RuntimeError(f"ADK service error {resp.status_code}: {resp.text}")

    # Try to interpret JSON responses first, then fallback to text
    text_out: str = ""
    try:
        data = resp.json()
        if isinstance(data, dict):
            # Heuristics across typical agent runtimes
            for key in ("output", "text", "message"):
                val = data.get(key)
                if isinstance(val, str) and val:
                    text_out = val
                    break
            if not text_out and "candidates" in data:
                # Gemini-like structure
                try:
                    text_out = (
                        data["candidates"][0]["content"]["parts"][0]["text"]
                    )
                except Exception:
                    pass
        if not text_out:
            text_out = resp.text or ""
    except ValueError:
        text_out = resp.text or ""

    if not text_out:
        text_out = (
            "I'm here with you. Could you share more about how you're feeling?"
        )
    return text_out


def run_therapy_session(user_id: str, message: str) -> str:
    """High-level API to run a therapy session turn.

    Builds context from Firestore, crafts a prompt, then calls the ADK agent API.
    Returns the assistant's reply text.
    """
    # Configure logger lazily for CLI/library usage
    logger = logging.getLogger("capymind_session")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    logger.info(
        "session start: project=%s emulator=%s user_id=%s",
        os.getenv("CAPY_PROJECT_ID"), os.getenv("FIRESTORE_EMULATOR_HOST"), user_id,
    )

    last_notes: List[str] = []
    try:
        last_notes = _get_last_notes(user_id, limit=5)
        logger.info("fetched %d last notes", len(last_notes))
        for i, n in enumerate(last_notes[:5], start=1):
            snippet = n if len(n) <= 300 else n[:300] + "..."
            logger.info("note %d: %s", i, snippet)
    except Exception:
        logger.exception("failed to fetch last notes from Firestore")
        last_notes = []

    try:
        locale = _get_user_locale(user_id)
    except Exception:
        logger.exception("failed to fetch user locale from Firestore; defaulting to en")
        locale = "en"
    language_name = "English" if locale == "en" else "Ukrainian"
    logger.info("using locale=%s language=%s", locale, language_name)

    prompt = _build_prompt(message, last_notes, language_name)

    try:
        response_text = _adk_api_reply(prompt, logger, session_id=user_id)
    except Exception:
        logger.exception("ADK API call failed; attempting Gemini fallback")
        try:
            response_text = _gemini_reply(prompt)
        except Exception:
            logger.exception("Gemini fallback failed; returning static fallback")
            response_text = (
                "I'm here with you. I wasn't able to access advanced tools just now, "
                "but I'd still like to help. Could you share more about how you're feeling?"
            )

    return response_text


def _parse_cli_args() -> Dict[str, Any]:
    import argparse

    parser = argparse.ArgumentParser(description="Run a CapyMind therapy session turn")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--message", required=True, help="User message text")
    args = parser.parse_args()
    return {"user_id": args.user_id, "message": args.message}


if __name__ == "__main__":
    params = _parse_cli_args()
    output = run_therapy_session(params["user_id"], params["message"])
    # Print plain text output
    print(output)