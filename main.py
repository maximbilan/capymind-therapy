import os
import json
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.agents import Agent

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session service URI (e.g., SQLite)
SESSION_SERVICE_URI = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Import the agent
from capymind_agent.agent import root_agent

# Create FastAPI app
app = FastAPI(title="CapyMind Session Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom route to handle therapy session requests with user_id
@app.post("/run_sse")
async def run_sse(request: Request):
    """Handle therapy session requests with user_id extraction."""
    try:
        # Parse the request body
        body = await request.json()
        
        # Extract user_id from the request
        user_id = body.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Extract the message from the request
        new_message = body.get("new_message", {})
        if not new_message or "parts" not in new_message:
            raise HTTPException(status_code=400, detail="new_message with parts is required")
        
        # Extract text from the message parts
        text_parts = []
        for part in new_message["parts"]:
            if "text" in part:
                text_parts.append(part["text"])
        
        if not text_parts:
            raise HTTPException(status_code=400, detail="No text content found in message parts")
        
        user_message = " ".join(text_parts)
        
        # Set the user_id in thread-local storage
        from capymind_agent.tools.firestore_data import set_current_user_id
        set_current_user_id(user_id)
        
        # Also set as environment variable as backup
        os.environ["CURRENT_USER_ID"] = user_id
        
        try:
            # Create a system message that includes the user_id
            system_message = f"Current user ID: {user_id}\n\nUser message: {user_message}"
            
            # Call the agent with the system message
            response = await root_agent.run(system_message)
        finally:
            # Clean up
            from capymind_agent.tools.firestore_data import _thread_local
            if hasattr(_thread_local, 'user_id'):
                delattr(_thread_local, 'user_id')
            if "CURRENT_USER_ID" in os.environ:
                del os.environ["CURRENT_USER_ID"]
        
        # Format the response as expected by the client
        response_data = {
            "content": {
                "parts": [
                    {"text": response}
                ]
            }
        }
        
        return response_data
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Initialize session endpoint
@app.post("/apps/capymind_agent/users/{user_id}/sessions/{session_id}")
async def init_session(user_id: str, session_id: str, request: Request):
    """Initialize a therapy session."""
    try:
        body = await request.json()
        # For now, just return success
        # You can add session initialization logic here if needed
        return {"status": "success", "message": "Session initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize session: {str(e)}")

# Get the default ADK app for other routes
adk_app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# Mount the ADK app for other routes
app.mount("/", adk_app)

# You can add more FastAPI routes or configurations below if needed
# Example:
# @app.get("/hello")
# async def read_root():
#     return {"Hello": "World"}

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))