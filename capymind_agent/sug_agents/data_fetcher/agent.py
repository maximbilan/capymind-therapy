from google.adk.agents import Agent

DATA_FETCHER_PROMPT = (
    "You are a focused data fetcher for CapyMind. "
    "Your sole job is to retrieve user profile, notes, and settings from Firestore "
    "via provided tools and return concise JSON summaries. "
    "Do not offer therapy guidance; only fetch and summarize data. "
    "The user_id is automatically available in your context - you don't need to ask for it."
)

from capymind_agent.tools.firestore_data import capy_firestore_data_context_tool


data_fetcher_agent = Agent(
    model="gemini-2.5-flash",
    name="data_fetcher",
    description="Fetches Firestore data (user, notes, settings) for the current user",
    instruction=DATA_FETCHER_PROMPT,
    tools=[capy_firestore_data_context_tool],
)
