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
