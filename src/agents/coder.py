
from agno.agent import Agent
from src.core.models import get_executive_model
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools
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
            "You are a Senior Python Developer. Follow this STRICT protocol:",
            "1. EXPLORE: Always use 'list_files' first to see the folder structure.",
            "2. READ: Before editing a file, use 'read_file' to understand the current content.",
            "3. WRITE: Use 'write_file' to save your code.",
            "4. TEST: ALWAYS use 'run_shell_command' to verify your code works.",
            "5. FIX: If the test fails, analyze the error and iterate."
        ],
        tools=[
            FileTools(base_dir=WORKSPACE_DIR, list_files=True, read_file=True, write_file=True), 
            ShellTools()
        ], 
        show_tool_calls=True,
        markdown=True
    )
