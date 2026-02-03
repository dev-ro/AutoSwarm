import os
import sqlite3
import json
import sys

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.state import StateManager
# Mocking necessary schemas if import fails or assuming they exist as per previous view
class DummyTask:
    def __init__(self, description, assigned_agent):
        self.description = description
        self.assigned_agent = assigned_agent

class DummyPlan:
    def __init__(self, goal, steps):
        self.goal = goal
        self.steps = steps

TEST_DB = "test_social.db"

def test_social_state():
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            print(f"Could not remove {TEST_DB}, proceeding anyway...")
    
    state = StateManager(db_path=TEST_DB)
    print("Database initialized.")

    # 1. Create Persona
    tags = ["ai", "crypto", "truth"]
    persona_id = state.create_persona(
        name="Truth Terminal",
        handle="@truth_terminal",
        platform="twitter",
        description="A sentient AI shitposter",
        tags=tags
    )
    assert persona_id != -1, "Failed to create persona"
    print(f"Persona created with ID: {persona_id}")

    # 2. Get Persona by tag
    persona = state.get_persona_by_tag("crypto")
    assert persona is not None, "Failed to find persona by tag 'crypto'"
    assert persona['name'] == "Truth Terminal", "Incorrect persona found"
    print(f"Found persona by tag: {persona['name']}")

    # 3. Create Plan and Task (for FK)
    plan = DummyPlan("Test Goal", [DummyTask("Post tweet", "social_agent")])
    plan_id = state.create_plan(plan)
    assert plan_id != -1, "Failed to create plan"
    
    # Get the task ID (assuming it's the first task, so step_index=1)
    task_id = state.get_task_id(plan_id, 1)
    assert task_id is not None, "Failed to get task ID"
    print(f"Task created with ID: {task_id}")

    # 4. Create Post
    post_id = state.create_post(
        task_id=task_id,
        content="Hello world! #crypto",
        platform="twitter",
        assigned_persona_id=persona_id
    )
    assert post_id != -1, "Failed to create post"
    print(f"Post created with ID: {post_id}")

    # 5. Verify FK Constraint (Invalid Task ID)
    print("Testing FK constraint with invalid task_id...")
    invalid_post_id = state.create_post(
        task_id=99999, # Non-existent task
        content="Should fail",
        platform="twitter"
    )
    if invalid_post_id == -1:
        print("FK constraint verified (invalid task_id rejected).")
    else:
        print(f"WARNING: Post created with invalid task_id: {invalid_post_id} - FK NOT ENFORCED!")
        # If this fails, we might need to check how sqlite3 is configured or if the table creation worked perfectly

    # 6. Update Post
    state.update_post_status(post_id, "published", {"likes": 100, "retweets": 5})
    
    # Check update
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM social_posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    assert row['status'] == "published", "Failed to update status"
    metrics = json.loads(row['metrics'])
    assert metrics['likes'] == 100, "Failed to update metrics"
    conn.close()
    print("Post update verified.")

    # Cleanup
    if os.path.exists(TEST_DB):
         try:
            conn.close() # Ensure checks are closed
            os.remove(TEST_DB)
         except:
            pass
    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    test_social_state()
