
from datetime import datetime
from agno.agent import Agent
from src.core.models import get_executive_model
from src.agents.schemas import Plan, PlanReview

def get_executive_agent() -> Agent:
    """
    Creates and returns the Executive Agent.
    This agent is responsible for high-level planning and task delegation.
    """
    current_date = datetime.now().strftime("%A, %B %d, %Y")

    return Agent(
        model=get_executive_model(),
        description="You are an Executive Agent acting as a Principal Software Architect.",
        instructions=[
            f"Context: Today is {current_date}.",
            "Analyze the user's high-level request.",
            "Break down the request into a series of actionable steps.",
            "Assign each step to a specific type of sub-agent: 'researcher', 'social', 'finance', 'coder', 'writer', 'editor'.",
            "Do NOT execute the steps yourself.",
            "You have access to a 'writer' agent (for drafting outlines, chapters, scripts, and saving files) and an 'editor' agent (for reviewing narrative structure and tone). Assign creative tasks to them.",
            "Ensure the plan is logical, sequential, and covers all aspects of the user's request.",
            # CRITICAL FIX: Explicitly force JSON since we disabled native structured_outputs
            "You MUST respond with a valid JSON object matching the Plan schema.",
            "Do NOT include markdown formatting like ```json ... ``` or additional text."
        ],
        output_schema=Plan,
        structured_outputs=False,
        markdown=True
    )

def get_plan_reviewer_agent() -> Agent:
    """
    Returns an agent specialized in reviewing and adapting plans.
    """
    current_date = datetime.now().strftime("%A, %B %d, %Y")

    return Agent(
        model=get_executive_model(),
        description="You are an Agile Project Manager and Strategist.",
        instructions=[
            f"Context: Today is {current_date}.",
            "Review the progress of the current plan.",
            "Analyze the result of the last completed step.",
            "Determine if the remaining steps are still valid or need to change.",
            "If the plan needs to change, provide a NEW Plan object containing ONLY the remaining steps.",
            "If the plan is fine, set should_modify to False.",
            "Be adaptive. If a research step failed, propose an alternative source or method."
        ],
        structured_outputs=True,
        markdown=True
    )
