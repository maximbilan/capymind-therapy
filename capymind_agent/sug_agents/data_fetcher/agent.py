from google.adk.agents import Agent

from capymind_agent.tools.firestore_data import firestore_data_tool
from capymind_agent.tools.format_data import format_data_tool
from capymind_agent.sug_agents.data_fetcher.prompt import DATA_FETCHER_PROMPT


data_fetcher_agent = Agent(
    model="gemini-2.5-flash",
    name="data_fetcher",
    description="Fetches Firestore data (user, notes, settings) for a given user_id and formats it into human-readable responses",
    instruction=DATA_FETCHER_PROMPT,
    tools=[firestore_data_tool, format_data_tool],
)
