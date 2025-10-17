#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/dev_adk_run.sh [AGENT_REF]
# Common refs: session_agent/agent.py:root_agent
AGENT_REF="${1:-session_agent/agent.py:root_agent}"

# Create venv if missing
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Upgrade pip and install deps
python -m pip install --upgrade pip
pip install -r requirements.txt

# Optional: install ADK CLI if not present
if ! command -v adk >/dev/null 2>&1; then
  echo "[info] 'adk' CLI not found. Installing google-adk..."
  pip install google-adk
fi

# Env hints (export before running if needed)
: "${CAPY_GEMINI_API_KEY:=}"
: "${CAPY_GEMINI_MODEL:=gemini-1.5-flash-latest}"
export CAPY_GEMINI_MODEL

# Run the agent via ADK, trying common CLI variants
set -x
if adk run "${AGENT_REF}"; then
  exit 0
fi

set +x
echo "[warn] 'adk run ${AGENT_REF}' failed. Trying alternative invocations..."
set -x
if adk chat "${AGENT_REF}"; then
  exit 0
fi

set +x
echo "[warn] 'adk chat ${AGENT_REF}' failed. Trying '--ref' flag..."
set -x
if adk run --ref "${AGENT_REF}"; then
  exit 0
fi

set +x
echo "[warn] Tried multiple ADK invocation styles without success."
echo "[hint] Verify your ADK version: 'adk --help' and subcommands (run/chat)."
echo "[hint] As a fallback, run the HTTP function locally:"
echo "       python -m functions_framework --target therapysession --port 8081"
exit 1
