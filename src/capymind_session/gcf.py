from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .agent import create_agent


def _cors_headers(origin: Optional[str]) -> Dict[str, str]:
    return {
        "Access-Control-Allow-Origin": origin or "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "3600",
    }


# Google Cloud Functions (HTTP) entry point
# Expected JSON payload: { "message": str, "history": [ {"role": "user"|"assistant", "content": str } ], "model": str }
# Response: { "reply": str }
# CORS preflight supported.

def agent_chat(request):  # type: ignore[override]
    origin = request.headers.get("Origin") if hasattr(request, "headers") else None
    headers = _cors_headers(origin)

    # Handle CORS preflight
    if getattr(request, "method", "").upper() == "OPTIONS":
        return ("", 204, headers)

    try:
        body = request.get_json(silent=True) or {}
    except Exception:
        body = {}

    user_text = body.get("message") or body.get("text")
    history = body.get("history")
    model = body.get("model")

    if not user_text or not isinstance(user_text, str):
        return (
            json.dumps({"error": "Missing 'message' in request body"}),
            400,
            {**headers, "Content-Type": "application/json"},
        )

    agent = create_agent(model=model)
    reply_text = agent.reply(user_text, history=history)

    return (
        json.dumps({"reply": reply_text}),
        200,
        {**headers, "Content-Type": "application/json"},
    )
