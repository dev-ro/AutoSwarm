import sys
import os
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from src.agents.manager import Manager
from src.agents.schemas import Plan, Task, AgentType

def test_manager_project_flow():
    print("Testing Manager Project Context Flow...")
    
    # Setup
    workspace_root = Path("./workspace")
    project_name = "IntegrationTestProject"
    project_dir = workspace_root / project_name
    
    if project_dir.exists():
        shutil.rmtree(project_dir)
        
    manager = Manager()
    
    # Create a Plan with project_default
    plan = Plan(
        goal="Write a test chapter",
        project_default=project_name,
        steps=[
            Task(
                description="Write a file named '01_test.md' with content 'Hello World'.",
                assigned_agent=AgentType.WRITER,
                # project_context should inherit from plan.project_default
            )
        ]
    )
    
    # Execute
    print(f"\n[1] Executing Plan for {project_name}...")
    manager.execute_plan(plan)
    
    # Verify
    expected_file = project_dir / "01_test.md"
    print(f"\n[2] Checking for file: {expected_file}")
    
    if expected_file.exists():
        print("[SUCCESS] File created in correct project folder.")
        print(f"Content: {expected_file.read_text()}")
    else:
        print("[FAILURE] File not found in project folder.")
        # Debug: list what is there
        if project_dir.exists():
            print(f"Contents of {project_dir}: {[x.name for x in project_dir.iterdir()]}")
        else:
            print("Project directory was not even created.")

if __name__ == "__main__":
    test_manager_project_flow()
