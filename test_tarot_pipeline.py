import os
import sys
import io
# Force UTF-8 encoding for stdout and stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.manager import Manager
from src.agents.schemas import Plan, Task, AgentType

def test_tarot_pipeline():
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("[ERROR] GOOGLE_API_KEY not found in .env file.")
        return

    print("=== SYNTHETIC TEST: Tarot Context Survival & Report Architecture ===")

    manager = Manager()

    synthetic_plan = Plan(
        goal="Generate an astrology and tarot report for John Doe (Jan 1, 1990) strictly enforcing the 4-node architecture.",
        project_default="TestTarotContext",
        steps=[
            Task(
                description="Fetch the celtic_cross spread for John Doe's current transits.",
                assigned_agent=AgentType.TAROT
            ),
            Task(
                description="Compile the final report using the drawn cards. Ensure you output exactly 4 nodes: 1. Executive Summary, 2. Astrology Diagnostic, 3. Tarot Diagnostic, 4. Actionable Mitigation Strategies. DO NOT DROP THE CARDS. Output straight to the user, DO NOT request approval.",
                assigned_agent=AgentType.WRITER
            )
        ]
    )

    plan_id = manager.execute_plan(synthetic_plan)
    
    # Save the final step result to a file so we can view it cleanly
    import sqlite3
    conn = sqlite3.connect('autoswarm.db')
    c = conn.cursor()
    # Find the last Writer task result for our current plan
    c.execute("SELECT result FROM tasks WHERE plan_id=? AND assigned_agent='writer' ORDER BY id DESC LIMIT 1", (plan_id,))
    res = c.fetchone()
    if res and res[0]:
        with open('final_report_output.txt', 'w', encoding='utf-8') as f:
            f.write(res[0])
    else:
        print("[WARNING] Could not find Writer result in DB for Plan ID:", plan_id)

    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_tarot_pipeline()
