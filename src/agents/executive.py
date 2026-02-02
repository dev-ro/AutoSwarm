
from agno.agent import Agent
from src.core.models import get_executive_model
from src.agents.schemas import Plan

def get_executive_agent() -> Agent:
    """
    Creates and returns the Executive Agent.
    This agent is responsible for high-level planning and task delegation.
    """
    return Agent(
        model=get_executive_model(),
        description="You are an Executive Agent acting as a Principal Software Architect.",
        instructions=[
            "Analyze the user's high-level request.",
            "Break down the request into a series of actionable steps.",
            "Assign each step to a specific type of sub-agent (e.g., 'Researcher', 'Coder', 'Tester').",
            "Do NOT execute the steps yourself.",
            "Ensure the plan is logical, sequential, and covers all aspects of the user's request."
        ],
        response_model=Plan,
        structured_outputs=True,
        markdown=True
    )
