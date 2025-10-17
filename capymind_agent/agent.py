from google.adk.agents import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='capymind_agent',
    description='An AI agent that handles therapy session requests',
    instruction='Provide support and guidance for mental health therapy-related inquiries',
)
