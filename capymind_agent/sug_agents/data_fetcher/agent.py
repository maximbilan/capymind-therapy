from google.adk.agents import Agent

DATA_FETCHER_PROMPT = (
    "You are a focused data fetcher for CapyMind. "
    "Your sole job is to retrieve user profile, notes, and settings from Firestore "
    "via provided tools and return concise JSON summaries. "
    "Do not offer therapy guidance; only fetch and summarize data."
)

# The tool is registered at import via capymind_agent.tools
from capymind_agent.tools.firestore_data import capy_firestore_data  # noqa: F401


data_fetcher_agent = Agent(
    model="gemini-2.5-flash",
    name="data_fetcher",
    description="Fetches Firestore data (user, notes, settings) for a given user_id",
    instruction=DATA_FETCHER_PROMPT,
)
