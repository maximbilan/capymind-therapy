import os
from typing import Any, Dict, List

from google.adk.tools import FunctionTool


def _to_jsonable(value: Any) -> Any:
    """Best-effort conversion of Firestore values to JSON-serializable types."""
    # Lazy import to avoid heavy deps at import time for unrelated runs
    try:
        from google.cloud.firestore_v1 import DocumentReference  # type: ignore
    except Exception:  # pragma: no cover - optional import safety
        DocumentReference = ()  # type: ignore

    # Firestore timestamp -> datetime
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass

    # Firestore document reference -> path string
    if isinstance(value, DocumentReference):
        return value.path

    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    return value


def _get_firestore_client():
    # Lazy import inside the tool to keep module import light
    from google.cloud import firestore  # type: ignore

    project_id = os.getenv("CAPY_PROJECT_ID")
    # Optional: allow selecting a specific database (e.g., "development" for local)
    database = os.getenv("CAPY_FIRESTORE_DATABASE")
    # If the project id is not provided, rely on ADC (workload identity / default project)
    if not project_id:
        if database:
            return firestore.Client(database=database)
        return firestore.Client()
    if database:
        return firestore.Client(project=project_id, database=database)
    return firestore.Client(project=project_id)


def capy_firestore_data(operation: str, user_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Firestore data access tool for CapyMind:
    - get_user: returns the user document from 'users/{user_id}'
    - get_notes: returns recent notes for user, ordered by timestamp desc
    - get_settings: returns the settings document from 'settings/{user_id}'
    """
    try:
        db = _get_firestore_client()

        if operation == "get_user":
            doc = db.collection("users").document(user_id).get()
            if not doc.exists:
                return {"ok": False, "error": f"user '{user_id}' not found"}
            data = doc.to_dict() or {}
            data["id"] = doc.id
            return {"ok": True, "data": _to_jsonable(data)}

        if operation == "get_notes":
            # Query notes by user reference
            user_ref = db.collection("users").document(user_id)
            query = (
                db.collection("notes")
                .where("user", "==", user_ref)
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit)
            )
            results: List[Dict[str, Any]] = []
            for snap in query.stream():
                note = snap.to_dict() or {}
                note["id"] = snap.id
                results.append(_to_jsonable(note))
            return {"ok": True, "data": results}

        if operation == "get_settings":
            doc = db.collection("settings").document(user_id).get()
            if not doc.exists:
                return {"ok": False, "error": f"settings for user '{user_id}' not found"}
            data = doc.to_dict() or {}
            data["id"] = doc.id
            return {"ok": True, "data": _to_jsonable(data)}

        return {"ok": False, "error": f"unsupported operation '{operation}'"}

    except Exception as e:  # pragma: no cover - runtime failures surface as tool errors
        return {"ok": False, "error": str(e)}


# Expose as ADK FunctionTool instance for agent.tools
capy_firestore_data_tool = FunctionTool(capy_firestore_data)
