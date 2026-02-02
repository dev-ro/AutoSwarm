from datetime import datetime
from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.browser import BrowserTools
from src.core.knowledge import get_knowledge_base

# --- NEW TOOL FOR AGENT TO USE ---
def save_to_knowledge_base(content: str, source: str = "User/Web") -> str:
    """
    Saves valuable information to the long-term Knowledge Base.
    Use this to store facts, research summaries, or technical specs.
    """
    try:
        kb = get_knowledge_base()
        # 'insert' creates a document and embeds it immediately
        kb.insert(
            text_content=content,
            metadata={
                "source": source,
                "date": datetime.now().isoformat()
            }
        )
        return "✅ Information saved to Knowledge Base."
    except Exception as e:
        return f"❌ Error saving to KB: {e}"

def get_research_agent() -> Agent:
    """
    Returns the Research Agent with Read/Write memory access.
    """
    knowledge_base = get_knowledge_base()
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    return Agent(
        model=get_executive_model(),
        description="You are a deep-dive investigator. Use the browser to find facts.",
        instructions=[
            f"Context: Today is {current_date}. THE YEAR IS 2026. DO NOT SEARCH FOR 2025.",
            "1. CHECK MEMORY: Always search your Knowledge Base first.",
            "2. SAVE FINDINGS: If you find new, useful info from the web, use 'save_to_knowledge_base' to store it.",
            "3. SYNTHESIZE: Combine web results with memory.",
            "4. CITE: When using memory, mention 'Recalled from Knowledge Base'."
        ],
        tools=[
            BrowserTools(), 
            save_to_knowledge_base # <--- Give it the "Write" tool
        ], 
        knowledge=knowledge_base,
        search_knowledge=True, # Allow it to "Read"
        markdown=True
    )
