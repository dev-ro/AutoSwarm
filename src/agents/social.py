from datetime import datetime
from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.social import SocialPublisher
from src.core.config import load_social_personas
from src.core.state import StateManager

def get_social_agent(state_manager: StateManager) -> Agent:
    """
    Returns the Social Agent with dynamic persona context.
    """
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    # Load Personas
    personas = load_social_personas()
    persona_context = "AVAILABLE PERSONAS:\n"
    if not personas:
        persona_context += "  - No personas configured. You are operating in default mode.\n"
    else:
        for p_id, p in personas.items():
            persona_context += f"  - ID: {p_id} | Handle: {p.handle} | Style: {p.style}\n"

    return Agent(
        model=get_executive_model(),
        description="You are a social media strategist managing multiple accounts.",
        instructions=[
            f"Context: Today is {current_date}.",
            "You understand 'vibe-coding' and modern internet culture.",
            "You manage the following personas:",
            persona_context,
            "When asked to post, select the most appropriate persona based on the requested 'vibe' or style.",
            "You MUST pass the persona's 'ID' to the tool when drafting a post.",
            "Draft posts that are engaging and suitable for the platform.",
            "NEVER submit a post without human confirmation (the tool only drafts).",
            "Be creative but professional (or 'edgy' if the vibe calls for it)."
        ],
        tools=[SocialPublisher(state_manager)],
        markdown=True
    )
