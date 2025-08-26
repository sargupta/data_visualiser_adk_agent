from google.adk.agents import Agent

test_agent = Agent(
    name="test_agent",
    model="gemini-2.5-pro",
    description="A simple test agent",
    instruction="You are a simple test agent.",
)
