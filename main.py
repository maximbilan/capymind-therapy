import json
import os
import logging
from typing import Dict, Any, List

import functions_framework
from session_agent.agent import root_agent
from google.cloud import firestore


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


@functions_framework.http
def therapysession(request):
    # Configure logger lazily (Cloud Functions adds handlers)
    logger = logging.getLogger("capymind_session")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    if request.method != "POST":
        return ("Only POST is supported", 405)

    try:
        payload: Dict[str, Any] = request.get_json(force=True, silent=False) or {}
    except Exception:
        return ("Invalid JSON", 400)

    user_id = payload.get("user_id")
    message = payload.get("message")
    if not user_id or not message:
        return ("Missing user_id or message", 400)

    logger.info(
        "therapysession request: project=%s emulator=%s user_id=%s",
        os.getenv("CAPY_PROJECT_ID"), os.getenv("FIRESTORE_EMULATOR_HOST"), user_id,
    )

    last_notes = []
    try:
        last_notes = _get_last_notes(user_id, limit=5)
        logger.info("fetched %d last notes", len(last_notes))
        for i, n in enumerate(last_notes[:5], start=1):
            snippet = n if len(n) <= 300 else n[:300] + "..."
            logger.info("note %d: %s", i, snippet)
    except Exception:
        # Fail-soft if Firestore is not accessible
        logger.exception("failed to fetch last notes from Firestore")
        last_notes = []
    # Fetch user locale and map to language name for the prompt
    try:
        locale = _get_user_locale(user_id)
    except Exception:
        logger.exception("failed to fetch user locale from Firestore; defaulting to en")
        locale = "en"
    language_name = "English" if locale == "en" else "Ukrainian"
    logger.info("using locale=%s language=%s", locale, language_name)

    prompt = _build_prompt(message, last_notes, language_name)

    try:
        # Use ADK agent; assume .run returns a string
        response_text = root_agent.run(prompt)
    except Exception as e:
        response_text = (
            "I'm here with you. I wasn't able to access advanced tools just now, "
            "but I'd still like to help. Could you share more about how you're feeling?"
        )

    return (response_text, 200, {"Content-Type": "text/plain; charset=utf-8"})