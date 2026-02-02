
from datetime import datetime
from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.social import SocialTools

def get_social_agent() -> Agent:
    """
    Returns the Social Agent.
    """
    current_date = datetime.now().strftime("%A, %B %d, %Y")

    return Agent(
        model=get_executive_model(),
        description="You are a social media strategist.",
        instructions=[
            f"Context: Today is {current_date}.",
            "You understand 'vibe-coding' and modern internet culture.",
            "Use 'monitor_topic' to gauge sentiment on a topic BEFORE drafting a post.",
            "When monitoring topics, always consider the current date to filter out old trends.",
            "Draft posts that are engaging and suitable for the platform.",
            "NEVER submit a post without human confirmation (the tool only drafts).",
            "Be creative but professional (or 'edgy' if the vibe calls for it)."
        ],
        tools=[SocialTools()],
        markdown=True
    )
