
from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.browser import BrowserTools

def get_research_agent() -> Agent:
    """
    Returns the Research Agent.
    """
    return Agent(
        model=get_executive_model(),
        description="You are a deep-dive investigator. Use the browser to find facts.",
        instructions=[
            "Use the 'search_web' tool to find information related to the task.",
            "Use the 'read_page' tool to gather details from promising links.",
            "If a page is blocked or fails, try a different source.",
            "Synthesize your findings into a concise summary.",
            "Do not make up facts. Cite your sources if possible."
        ],
        tools=[BrowserTools()],
        show_tool_calls=True,
        markdown=True
    )
