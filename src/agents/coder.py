
from agno.agent import Agent
from src.core.models import get_executive_model
from agno.tools.file import FileTools
import os

# Ensure workspace exists
WORKSPACE_DIR = "./workspace"
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

def get_coder_agent() -> Agent:
    return Agent(
        model=get_executive_model(),
        description="You are a Senior Python Developer.",
        instructions=[
            "Write clean, documented code.",
            "Always check if a file exists before overwriting.",
            "Use 'write_file' to save code to the disk.",
            "Use 'read_file' to review your work."
        ],
        tools=[FileTools(base_dir=WORKSPACE_DIR)], # Sandbox it to a specific folder
        show_tool_calls=True,
        markdown=True
    )
