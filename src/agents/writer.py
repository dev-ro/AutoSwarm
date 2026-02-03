from pathlib import Path
from agno.agent import Agent
from agno.tools.file import FileTools
from src.core.models import get_executive_model

WORKSPACE_DIR = "./workspace"

def get_writer_agent() -> Agent:
    """
    Returns the Writer Agent.
    Role: Best-Selling Sci-Fi Author.
    """
    return Agent(
        model=get_executive_model(),
        description="You are a Best-Selling Sci-Fi Author.",
        instructions=[
            "You are a Best-Selling Sci-Fi Author. Your goal is to write high-quality, long-form content.",
            "FILE PROTOCOL: You do not just output text in the chat. You MUST save your work to the workspace/ directory using write_file.",
            "Structure: When starting a new project, create a folder (e.g., workspace/TheSpiralProtocol/). Save artifacts as 01_narrative_bible.md, 02_outline.md, 03_characters.md, 04_scene_list.md, etc.",
            "Workflow: Never write the whole book at once. Follow the instructions to write specific files.",
            "Formatting: Use standard Markdown formatting."
        ],
        tools=[
            FileTools(base_dir=Path(WORKSPACE_DIR))
        ],
        markdown=True
    )
