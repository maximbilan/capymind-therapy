# CapyMind Session

Pocket therapist AI agent using Google ADK (optional) with Gemini fallback.

## Install

Ensure Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
# Optional ADK
pip install -e .[adk]
```

Set your Gemini API key if not using ADK or while ADK is experimental:

```bash
export CAPY_GEMINI_API_KEY=sk-...  # get from Google AI Studio
export CAPY_GEMINI_MODEL=gemini-1.5-flash-latest  # optional
```

## Usage

Interactive chat:

```bash
capymind-session chat
```

### Google Cloud Functions (HTTP) deployment

Create a simple function that exposes the agent as a REST API.

Entry point: `agent_chat` in `capymind_session/gcf.py`.

Deploy (2nd gen):

```bash
gcloud functions deploy capymind-agent-chat \
  --gen2 --runtime python312 --region us-central1 \
  --entry-point agent_chat --trigger-http --allow-unauthenticated \
  --set-env-vars CAPY_GEMINI_API_KEY=$CAPY_GEMINI_API_KEY,CAPY_GEMINI_MODEL=gemini-1.5-flash-latest
```

Invoke:

```bash
curl -X POST "https://REGION-PROJECT.cloudfunctions.net/capymind-agent-chat" \
  -H 'Content-Type: application/json' \
  -d '{"message": "I feel anxious before my meeting, can you help?"}'
```

Slash commands inside chat:
- `/journal <text>`: Save a private journal entry
- `/recent [n]`: Show last n journal entries (default 5)
- `/mood <label> <1-10>`: Log your mood
- `/moodsum [n]`: Show average intensity per mood over last n logs (default 20)
- `/plan <mood>`: Suggest coping strategies

Data is stored under `~/.capymind_session/`.

## Notes
- This assistant is not a replacement for a licensed therapist.
- In crisis, call your local emergency number or text/call 988 (US).
- ADK integration point is scaffolded in `capymind_session/agent.py` in `_adk_reply`.
