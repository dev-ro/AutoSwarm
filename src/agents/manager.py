
from typing import List
import re
from src.agents.schemas import Plan, Task, AgentType, PlanReview
from src.agents.researcher import get_research_agent, verify_knowledge
from src.agents.social import get_social_agent
from src.agents.finance import get_finance_agent
from src.agents.coder import get_coder_agent
from src.agents.executive import get_executive_agent, get_plan_reviewer_agent
from agno.agent import Agent
from src.core.models import get_executive_model
from src.core.state import StateManager

class Manager:
    """
    Manager class responsible for orchestrating the execution of the plan.
    It delegates tasks to the appropriate sub-agents with shared context.
    """
    def __init__(self):
        print("Manager initialized. Spinning up sub-agents...")
        self.executive = get_executive_agent()
        self.reviewer = get_plan_reviewer_agent()
        self.state_manager = StateManager()
        self.active_agents = {}
        
        # Simple evaluator for boolean checks (Plan-free)
        self.evaluator = Agent(
            model=get_executive_model(),
            instructions=["You are an evaluator. Reply with strictly 'YES' or 'NO'."],
            structured_outputs=False
        )

    def _get_agent(self, agent_type: AgentType) -> Agent:
        """Lazy loads agents to save memory."""
        if agent_type not in self.active_agents:
            if agent_type == AgentType.RESEARCHER:
                self.active_agents[agent_type] = get_research_agent(self.state_manager)
            elif agent_type == AgentType.SOCIAL:
                self.active_agents[agent_type] = get_social_agent(self.state_manager)
            elif agent_type == AgentType.FINANCE:
                self.active_agents[agent_type] = get_finance_agent()
            elif agent_type == AgentType.CODER:
                self.active_agents[agent_type] = get_coder_agent()
            elif agent_type == AgentType.REVIEWER:
                self.active_agents[agent_type] = get_plan_reviewer_agent()
            elif agent_type == AgentType.EXECUTIVE:
                self.active_agents[agent_type] = self.executive
            else:
                print(f"[WARNING] No handler for {agent_type}. Defaulting to Researcher.")
                self.active_agents[agent_type] = get_research_agent(self.state_manager)
        return self.active_agents[agent_type]

    def execute_plan(self, plan: Plan, resume_plan_id: int = None):
        """
        Iterates through the plan's steps and delegates them.
        Uses shared context memory and dynamic replanning logic.
        """
        print("\n" + "="*50)
        print(f" MANAGER: Executing Plan - {plan.goal}")
        print("="*50)
        
        plan_id = resume_plan_id
        if not plan_id:
            plan_id = self.state_manager.create_plan(plan)

        # CONTEXT MEMORY: Stores the results of all previous steps
        execution_context = f"Original Goal: {plan.goal}\n"

        current_step_index = 1
        while current_step_index <= len(plan.steps):
            task = plan.steps[current_step_index - 1]

            # 1. Resumption Check
            if resume_plan_id:
                 current_state = self.state_manager.get_active_plan()
                 if current_state:
                    db_task = next((t for t in current_state['tasks'] if t['step_index'] == current_step_index), None)
                    if db_task and db_task['status'] == 'completed':
                        print(f"[Step {current_step_index}] Already completed. Skipping.")
                        execution_context += f"\n\n[Step {current_step_index} Cached Result]:\n{db_task.get('result', 'No result found')}"
                        current_step_index += 1
                        continue

            self.state_manager.update_task_status(plan_id, current_step_index, "in_progress")
            
            # 2. Prepare the Prompt with Context
            # We append the history so the agent knows what the previous agents did
            full_prompt = (
                f"CURRENT TASK: {task.description}\n\n"
                f"--- CONTEXT FROM PREVIOUS STEPS ---\n"
                f"{execution_context}"
            )

            # 3. Delegate
            task_id = self.state_manager.get_task_id(plan_id, current_step_index)
            result = self.delegate_task(task, full_prompt, task_id)
            
            self.state_manager.update_task_status(plan_id, current_step_index, "completed", result=str(result))
            
            # 4. Update Context Memory
            execution_context += f"\n\n[Step {current_step_index} Result by {task.assigned_agent.value}]:\n{result}"
            
            # 5. OODA Loop / Review Phase
            if current_step_index < len(plan.steps):
                print(f"  [Review] Analyzing result of Step {current_step_index}...")
                
                remaining_steps_desc = [t.description for t in plan.steps[current_step_index:]]
                
                review_prompt = f"""
                Goal: {plan.goal}
                Step {current_step_index} Completed.
                Result: {result}
                
                Current Remaining Steps: {remaining_steps_desc}
                
                Does the plan need to change based on this result?
                """
                
                try:
                    review_response = self.reviewer.run(review_prompt, output_schema=PlanReview)
                    plan_review = review_response.content
                    
                    if plan_review.should_modify and plan_review.new_plan:
                        print(f"\n[PLAN CHANGE] Replanning triggered: {plan_review.reasoning}")
                        done_steps = plan.steps[:current_step_index]
                        new_steps = plan_review.new_plan.steps
                        plan.steps = done_steps + new_steps
                        print(f"  -> New Plan Length: {len(plan.steps)}")
                except Exception as e:
                    print(f"  [Review Error] Execution continuing regardless: {e}")

            current_step_index += 1
            
        print("\n" + "="*50)
        print(" MANAGER: Plan Execution Complete")
        print("="*50 + "\n")
        
        self.state_manager.complete_plan(plan_id)

    def delegate_task(self, task: Task, full_prompt: str, task_id: int = None) -> str:
        """
        Delegates a single task to the assigned agent type.
        """
        print(f"\n[AutoSwarm] Delegating to @{task.assigned_agent.value}...")
        print(f"  Task: {task.description}")
        
        agent = self._get_agent(task.assigned_agent)
        
        # --- Instrument Tools with Task Context ---
        if task_id and agent.tools:
            for tool in agent.tools:
                if hasattr(tool, 'set_task_context'):
                    tool.set_task_context(task_id)
        
        # --- Memory Leak Detection Setup ---
        kb_start_count = 0
        if task.assigned_agent == AgentType.RESEARCHER:
             kb_start_count = verify_knowledge()

        try:
            response = agent.run(full_prompt)
            result_content = response.content if hasattr(response, 'content') else str(response)
            
            print(f"\n  -> @{task.assigned_agent.value} Result:\n")
            print(result_content)

            # --- Artifact Extraction & Logging ---
            if task_id:
                # 1. Extract URLs with regex
                urls = re.findall(r'(https?://[^\s\)]+)', result_content)
                if urls:
                    print(f"  [Artifacts] Found {len(urls)} URLs. Logging...")
                    for url in urls:
                        # Log as a citation/source
                        self.state_manager.log_artifact(
                            task_id=task_id, 
                            artifact_type="citation", 
                            content=f"Extracted URL: {url}", 
                            source_url=url
                        )
                
                # 2. Heuristic: If it looks like a list of news items (lines starting with - or *), log them
                lines = result_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if (line.startswith('- ') or line.startswith('* ')) and len(line) > 20:
                         # basic heuristic for a "summary item" or "search result"
                         self.state_manager.log_artifact(
                            task_id=task_id,
                            artifact_type="summary_item",
                            content=line
                         )
                
                # --- [NEW] Memory Leak Check ---
                if task.assigned_agent == AgentType.RESEARCHER:
                    kb_end_count = verify_knowledge()
                    artifact_count = self.state_manager.get_artifact_count(task_id)
                    kb_delta = kb_end_count - kb_start_count
                    
                    if artifact_count > 0 and kb_delta == 0:
                        print("\n" + "!"*60)
                        print(" [WARNING] Memory Leak Detected: Agent found data but failed to save to KB.")
                        print(f"           Artifacts: {artifact_count} | KB Growth: 0")
                        print("!"*60 + "\n")
                    elif kb_delta > 0:
                        print(f"  [Memory] Knowledge Base grew by {kb_delta} documents.")

            # --- Human-in-the-Loop Trigger ---
            if "PENDING USER APPROVAL" in result_content:
                print("\n" + "!"*50)
                print(f" [STOP] User Approval Required for: {task.description}")
                print("!"*50)
                user_choice = input(">> Approve this action? (y/n/edit): ").strip().lower()
                if user_choice == 'y':
                    result_content = f"{result_content}\n[USER APPROVED]: Action authorized by human."
                elif user_choice == 'edit':
                    feedback = input(">> Enter instructions for revision: ")
                    return f"[USER REJECTED] Revision requested: {feedback}"
                else:
                    return "[USER REJECTED] Action denied."
            
            # --- Heuristic Gate / Semantic Handoff ---
            trigger_words = ["error", "fail", "urgent", "hiring", "job", "money", "profit", "crypto"]
            if any(w in result_content.lower() for w in trigger_words):
                handoff_check = self.evaluator.run(
                    f"Analyze this result from {task.assigned_agent.value}:\n\"{result_content[:500]}\"\n\n"
                    "Does this contain a high-value opportunity or critical failure? Reply ONLY 'YES' or 'NO'."
                )
                if "YES" in handoff_check.content.upper():
                    self._handle_handoff(result_content)
            else:
                print("  [Manager] Output standard. Skipping semantic handoff check.")

            return result_content

        except Exception as e:
            return f"Error executing task: {e}"

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
        response = self.executive.run(prompt, output_schema=Plan)
        
        if response.content and hasattr(response.content, 'goal'):
            new_plan = response.content
            print(f"  -> Executive Decision: {new_plan.goal}")
        else:
            print(f"  -> Executive Response: {response.content}")


