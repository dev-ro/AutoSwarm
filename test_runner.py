
import os
import sys
import time
from unittest.mock import patch
from dotenv import load_dotenv
from typing import List

# Ensure the src directory is in the python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.executive import get_executive_agent
from src.agents.manager import Manager
from src.agents.schemas import Plan

# Load environment variables
load_dotenv()

TEST_PROMPTS = [
    # Category 1: The "Builder"
    # "Write a Python script that prints the current timestamp every 5 seconds for 30 seconds. Save it as timer.py and execute it to verify it works.",
    # "Create a script that fetches the HTML title of 'example.com' and saves it to scraped_data.txt. Verify the file exists and contains data.",
    # "Read src/agents/schemas.py. Create a new file schemas_v2.py that adds a new AgentType called 'Tester'. Verify the new file is valid Python code by running it.",
    
    # Category 2: The "Truth Terminal"
    # "Research the top trending discussion on 'artificial intelligence' on Reddit or X today. Draft a provocative, viral-style tweet about it that fits the 'Truth Terminal' persona. Do not publish without my approval.",
    "Monitor sentiment around 'crypto regulation' from recent news articles. Summarize the general mood (Fear, Uncertainty, or Greed) and draft a LinkedIn post advising caution.",
    
    # Category 3: The "Hustler"
    "Search the web for 'Senior Python freelance contract remote'. If you find a job listing posted in the last 24 hours that mentions 'Generative AI', flag it for me immediately.",
    "I have 5 ETH. Check the current price of Ethereum. Research the risk of 'Restaking' protocols. Evaluate if I should move my funds there based on a risk tolerance of 4/10.",
    
    # Category 4: The "Deep Thinker"
    "Deep dive into the 'Model Context Protocol (MCP)'. Save the technical specifications and key integration patterns to your Knowledge Base so we don't have to look it up again.",
    "Based on your Knowledge Base, write a Python script that mocks a simple MCP server. Do not search the web; use what you remember.",
    
    # Category 5: Grand Plan
    "I want to launch a newsletter. 1. Research niche tech topics. 2. Create a content calendar for next week. 3. Write a Python script to manage subscribers in a CSV file."
]

def run_test(index: int, prompt: str, manager, executive):
    print(f"\n\n{'='*60}")
    print(f"TEST #{index + 1}: {prompt}")
    print(f"{'='*60}\n")
    
    try:
        print("[Test] Planning...")
        response = executive.run(prompt)
        plan = response.content
        
        if not isinstance(plan, Plan):
            print(f"[ERROR] Executive did not return a valid Plan object. Got: {type(plan)}")
            return False

        print(f"[Test] Plan Generated: {plan.goal} ({len(plan.steps)} steps)")
        
        # We patch 'input' to auto-approve requests
        # The manager asks: ">> Approve this action? (y/n/edit): "
        # We always return 'y'
        with patch('builtins.input', return_value='y'):
             manager.execute_plan(plan)
             
        print(f"\n[Test] Test #{index + 1} Completed Successfully.")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test #{index + 1} Failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("[ERROR] GOOGLE_API_KEY not found in env.")
        return

    print("Initializing Agents for Test Suite...")
    try:
        executive = get_executive_agent()
        manager = Manager()  # Resets state manager internally? No, need to be careful with DB state if needed.
    except Exception as e:
        print(f"FAILED to initialize agents: {e}")
        return

    results = []
    
    # Allow running specific test index via CLI arg (e.g., python test_runner.py 0)
    test_indices = range(len(TEST_PROMPTS))
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
            test_indices = [target]
        except ValueError:
            pass

    for i in test_indices:
        success = run_test(i, TEST_PROMPTS[i], manager, executive)
        results.append((i, success))
        # Small sleep between tests to let logs settle / avoid rate limits if any
        time.sleep(2)

    print("\n\n" + "="*30)
    print("TEST SUITE RESULTS")
    print("="*30)
    for i, success in results:
        status = "PASS" if success else "FAIL"
        print(f"Test #{i + 1}: {status}")

if __name__ == "__main__":
    main()
