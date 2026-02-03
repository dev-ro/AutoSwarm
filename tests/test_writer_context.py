import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.writer import get_writer_agent
from shutil import rmtree

def test_writer_isolation():
    print("Testing Writer Agent Isolation...")
    
    # Setup
    workspace_root = Path("./workspace")
    project_a = "TestProjectA"
    project_b = "TestProjectB"
    
    # Clean previous runs
    if (workspace_root / project_a).exists():
        rmtree(workspace_root / project_a)
    if (workspace_root / project_b).exists():
        rmtree(workspace_root / project_b)

    # 1. Instantiate Agent for Project A
    print(f"\n[1] Instantiating Writer for {project_a}...")
    writer_a = get_writer_agent(project_name=project_a, persona={"name": "SciFi Author"})
    
    # Check instructions
    print(f"  -> Agent Description: {writer_a.description}")
    assert project_a in writer_a.description
    
    # Check FileTools base_dir
    tools_a = writer_a.tools[0]
    print(f"  -> FileTools Base Dir: {tools_a.base_dir}")
    assert str(tools_a.base_dir).endswith(project_a)

    # 2. Instantiate Agent for Project B
    print(f"\n[2] Instantiating Writer for {project_b}...")
    writer_b = get_writer_agent(project_name=project_b, persona={"name": "Romance Author"})
    
    # Check instructions
    print(f"  -> Agent Description: {writer_b.description}")
    assert project_b in writer_b.description
    
    # Check FileTools base_dir
    tools_b = writer_b.tools[0]
    print(f"  -> FileTools Base Dir: {tools_b.base_dir}")
    assert str(tools_b.base_dir).endswith(project_b)

    print("\n[SUCCESS] Writer Agent correctly isolates projects.")

if __name__ == "__main__":
    test_writer_isolation()
