import os
import time
import logging
from typing import Any, Dict, List, Optional

from google.adk.tools import FunctionTool, ToolContext

# Module-level logger for Firestore tool
logger = logging.getLogger("capymind.firestore")

# Provide a sensible default handler if the host app did not configure logging.
# Users can control verbosity with CAPY_LOG_LEVEL (DEBUG, INFO, WARNING, ERROR).
if not logger.handlers:
    level_name = os.getenv("CAPY_LOG_LEVEL", "INFO").upper()
    try:
        level_value = getattr(logging, level_name, logging.INFO)
    except Exception:
        level_value = logging.INFO
    logger.setLevel(level_value)
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(_handler)
    logger.propagate = False


def _to_jsonable(value: Any) -> Any:
    """Best-effort conversion of Firestore values to JSON-serializable types."""
    # Lazy import to avoid heavy deps at import time for unrelated runs
    try:
        from google.cloud.firestore_v1 import DocumentReference  # type: ignore
    except ImportError:
        try:
            from google.cloud.firestore import DocumentReference  # type: ignore
        except ImportError:
            # Fallback if neither import works
            DocumentReference = ()  # type: ignore
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


def _get_firestore_client(
    override_project_id: Optional[str] = None,
    override_database: Optional[str] = None,
):
    # Lazy import inside the tool to keep module import light
    from google.cloud.firestore import Client as FirestoreClient
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError
    from google.auth.credentials import AnonymousCredentials

    # Determine project from explicit override or common environment variables.
    final_project = (
        override_project_id
        or os.getenv("FIRESTORE_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or "capymind"
    )

    client_kwargs: Dict[str, Any] = {
        "project": final_project,
    }

    # Try to get default credentials, but provide fallback if they're not available
    try:
        credentials, auth_project = default()
        client_kwargs["credentials"] = credentials
        # Use project from credentials if no override provided
        if not override_project_id and auth_project:
            client_kwargs["project"] = auth_project
            final_project = auth_project
        
            
    except DefaultCredentialsError:
        # No credentials available, use anonymous credentials as fallback
        # This allows the client to be created but will fail on actual operations
        client_kwargs["credentials"] = AnonymousCredentials()
        logger.warning(
            "No default credentials found. For local development, set GOOGLE_APPLICATION_CREDENTIALS "
            "to point to a service account key file, or run 'gcloud auth application-default login'. "
            "Using anonymous credentials (operations will fail with permission errors)."
        )
    except Exception as e:
        logger.warning(f"Unexpected error getting credentials: {e}, using anonymous credentials")
        client_kwargs["credentials"] = AnonymousCredentials()

    # Pass database only if provided and supported by the installed library.
    if override_database:
        try:
            return FirestoreClient(database=override_database, **client_kwargs)
        except TypeError:
            # Older firestore clients may not support the 'database' argument.
            pass

    return FirestoreClient(**client_kwargs)


def capy_firestore_data(
    operation: str,
    tool_context: ToolContext,
    limit: int = 10,
    project_id: Optional[str] = None,
    database: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Firestore data access tool for CapyMind:
    - get_user: returns the user document from 'users/{user_id}'
    - get_notes: returns recent notes for user, ordered by timestamp desc
    - get_settings: returns the settings document from 'settings/{user_id}'
    """
    start_ts = time.perf_counter()
    
    # Extract user_id from tool context
    try:
        user_id = tool_context._invocation_context.user_id
    except AttributeError:
        logger.error("ToolContext does not have _invocation_context.user_id")
        return {"ok": False, "error": "Unable to extract user_id from tool context"}
    
    # Determine the actual project that will be used
    actual_project = (
        project_id
        or os.getenv("FIRESTORE_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or "capymind"
    )
    
    # Determine the actual database that will be used
    actual_database = (
        database
        or os.getenv("FIRESTORE_DATABASE")
        or os.getenv("GOOGLE_CLOUD_DATABASE")
        or "(default)"
    )
    

    try:
        client_start_ts = time.perf_counter()
        db = _get_firestore_client(
            override_project_id=project_id,
            override_database=actual_database,
        )

        if operation == "get_user":
            op_start = time.perf_counter()
            doc = db.collection("users").document(user_id).get()
            if not doc.exists:
                return {"ok": False, "error": f"user '{user_id}' not found"}
            data = doc.to_dict() or {}
            data["id"] = doc.id
            result = {"ok": True, "data": _to_jsonable(data)}
            return result

        if operation == "get_notes":
            # Query notes by user reference
            user_ref = db.collection("users").document(user_id)
            from google.cloud.firestore import Query  # type: ignore
            query = (
                db.collection("notes")
                .where("user", "==", user_ref)
                .order_by("timestamp", direction=Query.DESCENDING)
                .limit(limit)
            )
            op_start = time.perf_counter()
            results: List[Dict[str, Any]] = []
            for snap in query.stream():
                note = snap.to_dict() or {}
                note["id"] = snap.id
                results.append(_to_jsonable(note))
            return {"ok": True, "data": results}

        if operation == "get_settings":
            op_start = time.perf_counter()
            doc = db.collection("settings").document(user_id).get()
            if not doc.exists:
                return {"ok": False, "error": f"settings for user '{user_id}' not found"}
            data = doc.to_dict() or {}
            data["id"] = doc.id
            result = {"ok": True, "data": _to_jsonable(data)}
            return result

        logger.warning("unsupported_operation op=%s user_id=%s", operation, user_id)
        return {"ok": False, "error": f"unsupported operation '{operation}'"}

    except Exception as e:  # pragma: no cover - runtime failures surface as tool errors
        # Emit full stack trace to aid debugging
        logger.exception(
            "capy_firestore_data:error op=%s user_id=%s project_id=%s database=%s",
            operation,
            user_id,
            actual_project,
            actual_database,
        )
        return {"ok": False, "error": str(e)}
    finally:
        pass


# Expose as ADK FunctionTool instance for agent.tools
firestore_data_tool = FunctionTool(capy_firestore_data)
