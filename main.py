import json
import os
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


def _build_prompt(user_message: str, last_notes: List[str]) -> str:
    history = "\n\n".join(f"- {n}" for n in last_notes) if last_notes else "(no prior notes)"
    return (
        "You are a supportive, empathetic therapist. Use the user's prior journal "
        "notes to personalize guidance. Keep responses concise, kind, and practical.\n\n"
        f"User message: {user_message}\n\n"
        f"Recent notes:\n{history}"
    )


@functions_framework.http
def therapysession(request):
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

    last_notes = []
    try:
        last_notes = _get_last_notes(user_id, limit=5)
    except Exception:
        # Fail-soft if Firestore is not accessible
        last_notes = []

    prompt = _build_prompt(message, last_notes)

    try:
        # Use ADK agent; assume .run returns a string
        response_text = root_agent.run(prompt)
    except Exception as e:
        response_text = (
            "I'm here with you. I wasn't able to access advanced tools just now, "
            "but I'd still like to help. Could you share more about how you're feeling?"
        )

    return (response_text, 200, {"Content-Type": "text/plain; charset=utf-8"})