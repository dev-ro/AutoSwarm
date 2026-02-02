
import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.executive import get_executive_agent
from src.agents.manager import Manager
from src.agents.schemas import Plan, Task, AgentType
from src.core.state import StateManager

def main():
    # 1. Load Environment Variables
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n[ERROR] GOOGLE_API_KEY not found in .env file.")
        print("Please create a .env file in the root directory with: GOOGLE_API_KEY=your_key")
        return

    print("Starting AutoSwarm System (Agno Framework)...")

    # 2. Initialize the Executive Agent
    try:
        executive = get_executive_agent()
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize Executive Agent: {e}")
        return

    # 3. Initialize the Manager and State Manager
    manager = Manager()
    state_manager = StateManager()

    print("\n[AutoSwarm] System Ready. I am an autonomous agent planner.")

    # Check for resumption
    active_state = state_manager.get_active_plan()
    if active_state:
        print(f"\n[RESUME NOTICE] Found an interrupted plan: '{active_state['plan']['goal']}'")
        choice = input("Do you want to resume this plan? (y/n): ").strip().lower()
        if choice == 'y':
            # Reconstruct Plan object
            # Note: tasks are dicts from DB, we need to convert them back to Task objects for the Manager logic
            # OR we can adjust the Manager to handle dicts. 
            # Ideally, we reconstruct the objects to match the type hint.
            tasks = []
            for t in active_state['tasks']:
                # Convert string from DB to Enum to satisfy Pydantic validation
                try:
                    agent_enum = AgentType(t['assigned_agent'])
                except ValueError:
                    # Fallback or error handling if DB has invalid value
                    print(f"Warning: Unknown agent type '{t['assigned_agent']}' in DB. Defaulting to Research.")
                    agent_enum = AgentType.RESEARCHER
                
                tasks.append(Task(description=t['description'], assigned_agent=agent_enum))
                
            resuned_plan = Plan(goal=active_state['plan']['goal'], steps=tasks)
            manager.execute_plan(resuned_plan, resume_plan_id=active_state['plan']['id'])
        else:
            # Mark as failed or just ignore? Let's ignore for now, user starts fresh.
            print("Starting fresh.")

    print("Enter your goal below (or type 'exit' to quit).")

    # 4. Main Event Loop
    while True:
        try:
            user_input = input("\n>>> Request: ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Shutting down AutoSwarm.")
                break
                
            if not user_input:
                continue

            print("\n(...) Executive Agent is planning...")
            
            # 5. Generate Plan
            # Using Agno's structured output capability
            response = executive.run(user_input)
            
            # Extract the Plan object from the response
            plan = response.content
            
            if not isinstance(plan, Plan):
                print(f"[ERROR] Agent did not return a valid Plan object. Got: {type(plan)}")
                # Fallback print of raw content if needed
                print(f"Raw response: {response.content}")
                continue

            print(f"[Plan Generated] Goal: {plan.goal}")
            print(f"               Steps: {len(plan.steps)}")

            # 6. Execute Plan
            manager.execute_plan(plan)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
