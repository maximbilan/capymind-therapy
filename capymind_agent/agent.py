from google.adk.agents import Agent
from capymind_agent.sug_agents.data_fetcher import data_fetcher_agent
from capymind_agent.tools.firestore_data import capy_firestore_data_context_tool

from capymind_agent.prompt import prompt

root_agent = Agent(
    model='gemini-2.5-flash',
    name='capymind_agent',
    description='An AI agent that handles therapy session requests',
    instruction=prompt,
    sub_agents=[data_fetcher_agent],
    tools=[capy_firestore_data_context_tool],
)
