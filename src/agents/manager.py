
from typing import List
from src.agents.schemas import Plan, Task, AgentType
from src.agents.researcher import get_research_agent
from src.agents.social import get_social_agent
from src.agents.finance import get_finance_agent
from src.agents.coder import get_coder_agent
from src.agents.executive import get_executive_agent, get_plan_reviewer_agent
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
        self.coder_agent = get_coder_agent()
        
        # We need the executive for handoffs
        self.executive = get_executive_agent()
        self.reviewer = get_plan_reviewer_agent()
        
        # State Manager
        self.state_manager = StateManager()

    def execute_plan(self, plan: Plan, resume_plan_id: int = None):
        """
        Iterates through the plan's steps and delegates them.
        Uses dynamic replanning logic.
        """
        print("\n" + "="*50)
        print(f" MANAGER: Executing Plan - {plan.goal}")
        print("="*50)
        
        plan_id = resume_plan_id
        if not plan_id:
            plan_id = self.state_manager.create_plan(plan)

        # Dynamic Execution Loop
        current_step_index = 1
        
        # We use a while loop because plan.steps might change length
        while current_step_index <= len(plan.steps):
            
            task = plan.steps[current_step_index - 1] # List is 0-indexed, index is 1-indexed

            # Check existing status for resumption
            if resume_plan_id:
                 current_state = self.state_manager.get_active_plan()
                 if current_state:
                    db_task = next((t for t in current_state['tasks'] if t['step_index'] == current_step_index), None)
                    if db_task and db_task['status'] == 'completed':
                        print(f"[Step {current_step_index}] Already completed. Skipping.")
                        current_step_index += 1
                        continue

            self.state_manager.update_task_status(plan_id, current_step_index, "in_progress")
            
            # Execute Task
            result = self.delegate_task(current_step_index, task)
            
            self.state_manager.update_task_status(plan_id, current_step_index, "completed", result=str(result))
            
            # --- OODA Loop / Review Phase ---
            # If there are steps remaining, check if we need to change them.
            if current_step_index < len(plan.steps):
                print(f"  [Review] Analyzing result of Step {current_step_index}...")
                
                remaining_steps_desc = [t.description for t in plan.steps[current_step_index:]]
                
                prompt = f"""
                Goal: {plan.goal}
                Step {current_step_index} Completed.
                Result: {result}
                
                Current Remaining Steps: {remaining_steps_desc}
                
                Does the plan need to change based on this result?
                """
                
                try:
                    review_response = self.reviewer.run(prompt)
                    plan_review = review_response.content
                    
                    if plan_review.should_modify and plan_review.new_plan:
                        print(f"\n[PLAN CHANGE] Replanning triggered: {plan_review.reasoning}")
                        
                        # Replace remaining steps
                        # We keep steps [0 .. current_step_index-1] (which are done)
                        # We append the new steps
                        done_steps = plan.steps[:current_step_index]
                        new_steps = plan_review.new_plan.steps
                        
                        plan.steps = done_steps + new_steps
                        
                        print(f"  -> New Plan Length: {len(plan.steps)}")
                        print(f"  -> Next Step: {new_steps[0].description if new_steps else 'None'}")
                    else:
                        print("  [Review] Plan good. Continuing...")
                        
                except Exception as e:
                    print(f"  [Review Error] Execution continuing regardless: {e}")

            current_step_index += 1
            
        print("\n" + "="*50)
        print(" MANAGER: Plan Execution Complete")
        print("="*50 + "\n")
        
        self.state_manager.complete_plan(plan_id)

    def delegate_task(self, index: int, task: Task) -> str:
        """
        Delegates a single task to the assigned agent type.
        Returns the result string.
        """
        print(f"\n[Step {index}] Delegating to @{task.assigned_agent.value}...")
        print(f"  Task: {task.description}")
        
        response = None
        
        # Routing logic using Enums
        # task.assigned_agent is now an Enum member
        
        if task.assigned_agent == AgentType.RESEARCHER:
            print(f"  -> Activating ResearchAgent...")
            response = self.researcher.run(task.description)
        elif task.assigned_agent == AgentType.SOCIAL:
            print(f"  -> Activating SocialAgent...")
            response = self.social_agent.run(task.description)
        elif task.assigned_agent == AgentType.FINANCE:
            print(f"  -> Activating FinanceAgent...")
            response = self.finance_agent.run(task.description)
        elif task.assigned_agent == AgentType.CODER:
            print(f"  -> Activating CoderAgent...")
            response = self.coder_agent.run(task.description)
        else:
            print(f"  -> [WARNING] No specific handler for '{task.assigned_agent}'. Defaulting to ResearchAgent.")
            response = self.researcher.run(task.description)

        result_content = "No response"
        if response:
            result_content = response.content
            print(f"\n  -> @{task.assigned_agent.value} Result:\n")
            print(result_content)

            # --- NEW: Human-in-the-Loop Trigger ---
            if "PENDING USER APPROVAL" in result_content:
                print("\n" + "!"*50)
                print(f" [STOP] User Approval Required for: {task.description}")
                print(f" Agent Output: {result_content}")
                print("!"*50)
                
                user_choice = input(">> Approve this action? (y/n/edit): ").strip().lower()
                
                if user_choice == 'y':
                    # In a real system, you would call a 'publish_post' tool here.
                    # For now, we simulate the 'signing' of the action.
                    result_content = f"{result_content}\n[USER APPROVED]: Action authorized by human."
                elif user_choice == 'edit':
                    feedback = input(">> Enter instructions for revision: ")
                    return f"[USER REJECTED] Revision requested: {feedback}"
                else:
                    return "[USER REJECTED] Action denied."
            
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


