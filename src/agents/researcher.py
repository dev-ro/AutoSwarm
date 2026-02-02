
from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.browser import BrowserTools
from src.core.knowledge import get_knowledge_base

def get_research_agent() -> Agent:
    """
    Returns the Research Agent.
    """
    knowledge_base = get_knowledge_base()
    
    return Agent(
        model=get_executive_model(),
        description="You are a deep-dive investigator. Use the browser to find facts.",
        instructions=[
            "Always search your Knowledge Base first before browsing the web.",
            "If you find relevant info in the KB, use it.",
            "If not, use the 'search_web' tool.",
            "Use the 'read_page' tool to gather details from promising links.",
            "If a page is blocked or fails, try a different source.",
            "Synthesize your findings into a concise summary.",
            "Do not make up facts. Cite your sources if possible.",
            "Save useful technical documentation to the Knowledge Base (Use the provided knowledge tools)."
        ],
        tools=[BrowserTools()], 
        knowledge=knowledge_base,
        markdown=True
    )
