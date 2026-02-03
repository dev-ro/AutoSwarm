from datetime import datetime
from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.browser import BrowserTools
from src.core.knowledge import get_knowledge_base

# --- NEW TOOL FOR AGENT TO USE ---
import uuid

def save_to_knowledge_base(content: str, source: str = "User/Web") -> str:
    """
    Saves valuable information to the long-term Knowledge Base.
    Use this to store facts, research summaries, or technical specs.
    """
    try:
        kb = get_knowledge_base()
        # Explicitly generate a unique name to ensure we append, not overwrite/update.
        # We use a UUID to guarantee uniqueness.
        doc_name = f"{source}_{uuid.uuid4()}"
        
        # 'insert' creates a document and embeds it immediately
        kb.insert(
            text_content=content,
            name=doc_name,
            metadata={
                "source": source,
                "date": datetime.now().isoformat()
            }
        )
        return "✅ Information saved to Knowledge Base."
    except Exception as e:
        return f"❌ Error saving to KB: {e}"

def verify_knowledge() -> int:
    """
    Checks the integrity of the Knowledge Base.
    Returns the count of documents currently stored.
    """
    try:
        kb = get_knowledge_base()
        # Ensure connection/table
        if not kb.vector_db.exists():
            print("[Knowledge Base] Not initialized yet.")
            return 0
            
        # Access the table directly from the vector db 
        # (Assuming LanceDB implementation in Agno allows accessing the table)
        # We catch potential errors if table doesn't exist yet
        # Access the table directly from the vector db 
        # (Assuming LanceDB implementation in Agno allows accessing the table)
        # We catch potential errors if table doesn't exist yet
        tbl = kb.vector_db.table
        if not tbl:
             print("[Knowledge Base] Table empty or not found.")
             return 0
             
        count = len(tbl.to_pandas())
        print(f"[Knowledge Base Integrity Check] Found {count} documents.")
        return count
    except Exception as e:
        print(f"[Knowledge Base] Verification Error: {e}")
        return 0

def get_research_agent(state_manager=None) -> Agent:
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
            "2. SAVE FINDINGS: Every successful research step MUST end by calling save_to_knowledge_base with a summary of findings.",
            "3. SYNTHESIZE: Combine web results with memory.",
            "4. CITE: When using memory, mention 'Recalled from Knowledge Base'."
        ],
        tools=[
            BrowserTools(state_manager=state_manager), 
            save_to_knowledge_base # <--- Give it the "Write" tool
        ], 
        knowledge=knowledge_base,
        search_knowledge=True, # Allow it to "Read"
        markdown=True
    )
