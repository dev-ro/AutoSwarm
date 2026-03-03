from typing import Optional, Dict, Any
from pathlib import Path
from agno.agent import Agent
from agno.tools.file import FileTools
from src.core.models import get_executive_model
from src.tools.google_docs import GoogleDocsTools

WORKSPACE_ROOT = "./workspace"

def get_writer_agent(project_name: str = "general", persona: Optional[Dict[str, Any]] = None) -> Agent:
    """
    Returns a configured Writer Agent based on the project context and persona.
    
    Args:
        project_name (str): The name of the project folder (e.g., "TheSpiralProtocol").
        persona (dict): Only needs 'name' and 'system_prompt_template' keys.
    """
    
    # 1. Determine Project Directory
    project_dir = Path(WORKSPACE_ROOT) / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Determine Persona
    if not persona:
        persona = {
            "name": "Generic Writer",
            "system_prompt_template": "You are a versatile professional writer. Adapt your style to the user's request."
        }
    
    agent_name = persona.get("name", "Writer")
    prompt_template = persona.get("system_prompt_template", "You are a helpful writer.")
    
    # 3. Construct Instructions
    instructions = [
        f"You are {agent_name}.",
        prompt_template,
        "--- FILE PROTOCOL ---",
        f"1. You are working in the project: '{project_name}'.",
        f"2. YOUR WORKSPACE ROOT IS: workspace/{project_name}/",
        "3. You MUST save significant work to files.",
        "4. DO NOT create nested workspace folders (e.g., workspace/workspace/...). All paths are relative to your root.",
        "5. Structure your project logically (e.g., 01_concept.md, 02_outline.md).",
        "--- END PROTOCOL ---",
        "--- ASTROLOGY & TAROT REPORTING RULES ---",
        "If you are requested to compile an Astrology or Tarot report, YOU MUST strictly enforce the following 4-node architecture:",
        "1. Executive Summary: High-level overview of the day's energy.",
        "2. Astrology Diagnostic: Technical breakdown of transits and aspects.",
        "3. Tarot Diagnostic: Detailed analysis of the DRAWN CARDS. You MUST include the raw card names and positions exactly as provided by the TarotAgent in the context. DO NOT draw new cards, do not modify the names, and do not hallucinate different results.",
        "4. Actionable Mitigation Strategies: Practical steps to handle difficulties.",
        "CRITICAL: YOUR ROLE IS A SYNTHESIZER. You must treat the data from previous steps as the GROUND TRUTH. If you find cards in the context, you MUST use those specific cards and no others.",
        "IMPORTANT: When instructed to output to Google Docs, use the `post_to_google_doc` tool after generating your response.",
        "--- END REPORTING RULES ---"
    ]

    return Agent(
        model=get_executive_model(),
        description=f"You are {agent_name}, working on {project_name}.",
        instructions=instructions,
        tools=[
            FileTools(base_dir=project_dir),
            GoogleDocsTools()
        ],
        markdown=True
    )
