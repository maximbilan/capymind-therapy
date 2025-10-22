from google.adk.agents import Agent
from google.adk.tools import google_search

from capymind_agent.tools.firestore_data import firestore_data_tool
from capymind_agent.sug_agents.crysis_line.prompt import CRISIS_LINE_PROMPT


crisis_line_agent = Agent(
    model="gemini-2.5-flash",
    name="crisis_line",
    description="Finds crisis line phone numbers for users in critical situations based on their location",
    instruction=CRISIS_LINE_PROMPT,
    tools=[firestore_data_tool, google_search],
)