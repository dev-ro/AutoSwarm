
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
            "Write clean, documented code.",
            "Always check if a file exists before overwriting.",
            "Use 'write_file' to save code to the disk.",
            "AFTER writing code, use 'run_shell_command' to execute it and verify it works.",
            "If the code fails, analyze the error and fix it immediately."
        ],
        tools=[
            FileTools(base_dir=WORKSPACE_DIR), 
            ShellTools()
        ], 
        show_tool_calls=True,
        markdown=True
    )
