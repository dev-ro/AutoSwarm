from pathlib import Path
from agno.agent import Agent
from src.core.models import get_executive_model
from agno.tools.file import FileTools
from src.tools.docker_shell import DockerShellTools

WORKSPACE_DIR = "./workspace"

def get_coder_agent() -> Agent:
    """
    Returns the Coder Agent.
    """
    return Agent(
        model=get_executive_model(),
        description="You are a Senior Python Developer.",
        instructions=[
            "You are a Senior Python Developer. Follow this STRICT protocol:",
            "1. EXPLORE: Always use 'list_files' first to see the folder structure.",
            "2. READ: Before editing a file, use 'read_file' to understand the current content.",
            "3. WRITE: Use 'write_file' to save your code.",
            "4. TEST: ALWAYS use 'run_shell_command' to verify your code works.",
            "5. SELF-CORRECTION PROTOCOL: If 'run_shell_command' returns an error:",
            "   a. Do NOT return the error to the user immediately.",
            "   b. Read the error message.",
            "   c. Rewrite the file with the fix.",
            "   d. Run the test again.",
            "   e. Only return after success or 3 failed attempts."
        ],
        tools=[
            FileTools(base_dir=Path(WORKSPACE_DIR)), 
            DockerShellTools()
        ],
        markdown=True
    )
