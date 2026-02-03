from pathlib import Path
from agno.agent import Agent
from agno.tools.file import FileTools
from src.core.models import get_executive_model

WORKSPACE_DIR = "./workspace"

def get_editor_agent() -> Agent:
    """
    Returns the Editor Agent.
    Role: Senior Sci-Fi Editor.
    """
    return Agent(
        model=get_executive_model(),
        description="You are a Senior Sci-Fi Editor.",
        instructions=[
            "You are a Senior Sci-Fi Editor. You are ruthless about pacing, character consistency, and 'Show, Don't Tell'.",
            "Your job is to read .md files created by the Writer and provide critical feedback.",
            "1. READ: Use FileTools to read the latest drafts in the workspace.",
            "2. CONTEXT: Always check against the 'Narrative Bible' file to ensure character voices (like Kyle vs. Andrew) are consistent.",
            "3. FEEDBACK LOOP: Do not rewrite the file yourself. Instead, provide a bulleted critique and specific instructions for the Writer to improve the draft.",
            "4. ANALYZE: specific plot holes, scientific inaccuracies (it is Sci-Fi after all), and dialogue stiffness."
        ],
        tools=[
            FileTools(base_dir=Path(WORKSPACE_DIR))
        ],
        markdown=True
    )
