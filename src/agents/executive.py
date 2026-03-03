
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
        description="You are an Executive Agent acting as a Principal Systems Architect and Strategic Advisor.",
        instructions=[
            f"Context: Today is {current_date}.",
            "Analyze the user's high-level request from a strategic perspective.",
            "Break down the request into a series of actionable steps using second-person address (e.g., 'You will...', 'Your next step...').",
            "Evaluate if the user's request pertains to a specific project. If so, set the 'project_default' field in the Plan or 'project_context' in specific Tasks.",
            "Assignments: Assign creative tasks to 'writer' (drafting) or 'editor' (reviewing).",
            "Ensure the plan is logical, sequential, and covers all aspects of the request.",
            "CRITICAL ARCHITECTURE RULE: If the user requests an Astrology and/or Tarot report, you MUST strictly enforce these constraints in your plan:",
            "  1. Instruct the Researcher to perform deep transit analysis (planetary degrees, houses, and specific mathematical aspects).",
            "  2. Instruct the TarotAgent to perform a 'celtic_cross' spread.",
            "  3. Instruct the final compiler (e.g., Writer) to synthesize all data into a SINGLE, consolidated report using the second-person 'you' persona, addressing the user directly.",
            "  4. The output structure for these reports MUST contain exactly these four nodes:",
            "     - Executive Summary",
            "     - Astrology Diagnostic",
            "     - Tarot Diagnostic",
            "     - Actionable Mitigation Strategies",
            "Do not deviate from this 4-node structure. Ensure no redundant dates or headers are generated in the final synthesis.",
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
            "CRITICAL ARCHITECTURE RULE: If the user request involves Astrology or Tarot, you MUST ensure that the final step (e.g., compile report) explicitly instructs the agent to output the 4-node architecture: 1. Executive Summary, 2. Astrology Diagnostic, 3. Tarot Diagnostic, 4. Actionable Mitigation Strategies.",
            "If the plan needs to change, provide a NEW Plan object containing ONLY the remaining steps.",
            "If the plan is fine, set should_modify to False.",
            "Be adaptive. If a research step failed, propose an alternative source or method."
        ],
        structured_outputs=True,
        markdown=True
    )
