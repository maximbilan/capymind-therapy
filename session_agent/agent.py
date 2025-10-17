try:
    from google.adk.agents.llm_agent import Agent
except Exception:  # pragma: no cover
    class Agent:  # minimal fallback if ADK is unavailable
        def __init__(self, model: str, name: str, description: str, instruction: str):
            self.model = model
            self.name = name
            self.description = description
            self.instruction = instruction

        def run(self, prompt: str) -> str:
            return (
                "I'm listening. While my advanced tools are unavailable, I can still "
                "support you. Tell me more about what's going on."
            )
except Exception:  # pragma: no cover
    class Agent:  # minimal fallback
        def __init__(self, model: str, name: str, description: str, instruction: str):
            self.model = model
            self.name = name
            self.description = description
            self.instruction = instruction

        def run(self, prompt: str) -> str:
            return (
                "I'm listening. While my advanced tools are unavailable, I can still "
                "support you. Tell me more about what's going on."
            )

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='An AI agent that handles therapy session requests',
    instruction='Provide support and guidance for mental health therapy-related inquiries',
)
