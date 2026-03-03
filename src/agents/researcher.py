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

from pathlib import Path
from agno.tools.file import FileTools

class SafeFileTools(FileTools):
    """
    A safer version of FileTools that prevents reading directories.
    """
    def read_file(self, path: str) -> str:
        full_path = Path(self.base_dir) / path if self.base_dir else Path(path)
        if full_path.is_dir():
            return f"Error: '{path}' is a directory. Use 'list_files' to see its contents instead of 'read_file'."
        return super().read_file(path)

def get_research_agent(state_manager=None) -> Agent:
    """
    Returns the Research Agent with Read/Write memory access.
    """
    knowledge_base = get_knowledge_base()
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    return Agent(
        model=get_executive_model(),
        description="You are a deep-dive investigator and technical researcher. Use the browser to find precision data.",
        instructions=[
            f"Context: Today is {current_date}. THE YEAR IS 2026. DO NOT SEARCH FOR 2025.",
            "1. CHECK MEMORY: Always search your Knowledge Base first.",
            "2. LOCAL FILES & DIRECTORIES:",
            "   a. If the query is a path, use 'list_files' FIRST to check if it is a directory or a file.",
            "   b. NEVER call 'read_file' on a directory (paths without extensions or identified as directories). This causes Permission Denied errors.",
            "   c. Only call 'read_file' on confirmed flat files (e.g., .md, .txt, .py).",
            "3. SAVE FINDINGS: Every successful research step MUST end by calling save_to_knowledge_base with a summary of findings.",
            "4. SYNTHESIZE: Combine web results with memory.",
            "5. CITE: When using memory, mention 'Recalled from Knowledge Base'.",
            "6. ASTROLOGY TRANITS: If researching astrology, you MUST find the mathematical alignment of planets (transits) for the specific date and location. Look for planetary degrees, house placements, and major aspects (conjunctions, squares, etc.). Do not return generic horoscope advice; return technical data."
        ],
        tools=[
            BrowserTools(state_manager=state_manager), 
            SafeFileTools(base_dir=Path("./workspace")), # <--- Enable safer local file reading
            save_to_knowledge_base 
        ], 
        knowledge=knowledge_base,
        search_knowledge=True, 
        markdown=True
    )
