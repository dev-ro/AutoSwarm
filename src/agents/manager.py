
from typing import List
from src.agents.schemas import Plan, Task
from src.agents.researcher import get_research_agent
from src.agents.social import get_social_agent
from src.agents.finance import get_finance_agent
from src.agents.executive import get_executive_agent # Self-referential for handoff
from src.core.state import StateManager

class Manager:
    """
    Manager class responsible for orchestrating the execution of the plan.
    It delegates tasks to the appropriate sub-agents.
    """
    def __init__(self):
        # Initialize sub-agents
        print("Manager initialized. Spinning up sub-agents...")
        self.researcher = get_research_agent()
        self.social_agent = get_social_agent()
        self.finance_agent = get_finance_agent()
        
        # We need the executive for handoffs
        self.executive = get_executive_agent()
        
        # State Manager
        self.state_manager = StateManager()

    def execute_plan(self, plan: Plan, resume_plan_id: int = None):
        """
        Iterates through the plan's steps and delegates them.
        If resume_plan_id is provided, it uses existing state.
        Otherwise, it creates a new plan in state.
        """
        print("\n" + "="*50)
        print(f" MANAGER: Executing Plan - {plan.goal}")
        print("="*50)
        
        plan_id = resume_plan_id
        if not plan_id:
            plan_id = self.state_manager.create_plan(plan)

        for i, task in enumerate(plan.steps, 1):
            # Check current status in DB to see if we should skip
            # In a resume scenario, we need to know if this step is already done.
            # For simplicity in this loop, we just re-check the DB or rely on the passed-in logic.
            # But efficiently, we should check `self.state_manager.get_active_plan()`
            # Here we assume the loop is running sequentially.
            
            # Let's verify status from DB if resuming
            if resume_plan_id:
                current_state = self.state_manager.get_active_plan()
                if current_state:
                    db_task = next((t for t in current_state['tasks'] if t['step_index'] == i), None)
                    if db_task and db_task['status'] == 'completed':
                        print(f"[Step {i}] Already completed. Skipping.")
                        continue

            self.state_manager.update_task_status(plan_id, i, "in_progress")
            
            # Execute
            result = self.delegate_task(i, task)
            
            self.state_manager.update_task_status(plan_id, i, "completed", result=str(result))
            
        print("\n" + "="*50)
        print(" MANAGER: Plan Execution Complete")
        print("="*50 + "\n")
        
        self.state_manager.complete_plan(plan_id)

    def delegate_task(self, index: int, task: Task) -> str:
        """
        Delegates a single task to the assigned agent type.
        Returns the result string.
        """
        print(f"\n[Step {index}] Delegating to @{task.assigned_agent}...")
        print(f"  Task: {task.description}")
        
        response = None
        
        # Routing logic
        agent_type = task.assigned_agent.lower()
        
        if "research" in agent_type:
            print(f"  -> Activating ResearchAgent...")
            response = self.researcher.run(task.description)
        elif "social" in agent_type or "media" in agent_type:
            print(f"  -> Activating SocialAgent...")
            response = self.social_agent.run(task.description)
        elif "finance" in agent_type or "wallet" in agent_type:
            print(f"  -> Activating FinanceAgent...")
            response = self.finance_agent.run(task.description)
        else:
            print(f"  -> [WARNING] No specific agent found for '{task.assigned_agent}'. Defaulting to ResearchAgent.")
            response = self.researcher.run(task.description)

        result_content = "No response"
        if response:
            result_content = response.content
            print(f"\n  -> @{task.assigned_agent} Result:\n")
            print(result_content)
            
            # HANDOFF LOGIC
            # Check for triggers to pass back to Executive
            if "freelance" in result_content.lower() and ("job" in result_content.lower() or "hiring" in result_content.lower()):
                self._handle_handoff(result_content)

        return result_content

    def _handle_handoff(self, content: str):
        """
        Handles the handoff from a sub-agent to the Executive Agent.
        """
        print("\n" + "!"*50)
        print(" HANDOFF TRIGGERED: Potential Opportunity Detected")
        print("!"*50)
        
        prompt = f"""
        A sub-agent found the following information which requires your decision:
        
        "{content}"
        
        Analyze this opportunity. Should we apply or take action? 
        If yes, create a short plan (1-2 steps) to proceed. If no, explain why.
        """
        
        print("  -> Asking Executive Agent for decision...")
        response = self.executive.run(prompt)
        
        # The executive returns a Plan object (structured output)
        # We can recursively execute this new mini-plan or just print it for now.
        if response.content and hasattr(response.content, 'goal'):
            new_plan = response.content
            print(f"  -> Executive Decision: {new_plan.goal}")
            # Optional: Recursive execution
            # self.execute_plan(new_plan) 
            # (Prevent infinite recursion in robust systems, but okay for demo)
        else:
            print(f"  -> Executive Response: {response.content}")


