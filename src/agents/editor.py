from pathlib import Path
from agno.agent import Agent
from agno.tools.file import FileTools
from src.core.models import get_executive_model

WORKSPACE_DIR = "./workspace"

def get_editor_agent(project_name: str = "General", persona: dict = None) -> Agent:
    """
    Returns the Editor Agent.
    Role: Adapts to the provided persona or defaults to a Senior Editor.
    """
    if persona:
        role = persona.get("role", "Senior Editor")
        base_instructions = persona.get("instructions", [
            "You are a Senior Editor.",
            "Your job is to read drafts and provide critical feedback based on the project's style guide."
        ])
    else:
        role = "Senior Editor"
        base_instructions = [
            "You are a Senior Editor. You are ruthless about pacing, clarity, and structure.",
            "Your job is to read .md files created by the Writer and provide critical feedback.",
            "1. READ: Use FileTools to read the latest drafts in the workspace.",
            "2. CONTEXT: Check for consistency in tone and voice.",
            "3. FEEDBACK LOOP: Do not rewrite the file yourself. Instead, provide a bulleted critique and specific instructions for the Writer.",
            "4. ANALYZE: specific gaps, logic errors, and flow issues."
        ]

    instructions = [
        f"Context: Project '{project_name}'",
        f"Role: {role}"
    ] + base_instructions

    return Agent(
        model=get_executive_model(),
        description=f"You are a {role}.",
        instructions=instructions,
        tools=[
            FileTools(base_dir=Path(WORKSPACE_DIR))
        ],
        markdown=True
    )
