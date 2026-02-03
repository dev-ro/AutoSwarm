import os
import sys
import unittest
import sqlite3
from unittest.mock import patch, MagicMock

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import SocialPersona
from src.core.state import StateManager
from src.tools.social import SocialPublisher

class TestSocialPublisher(unittest.TestCase):
    def setUp(self):
        # Setup temporary DB
        self.db_path = "test_social_publisher.db"
        
        # Cleanup from previous run if needed
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass # Ignore if locked, might cause issues but usually okay for overwriting

        self.state_manager = StateManager(db_path=self.db_path)
        self.publisher = SocialPublisher(self.state_manager)
        
        # --- SEED DB WITH DEPENDENCIES (FK Constraints) ---
        from src.agents.schemas import Plan, Task, AgentType
        
        # 1. Create Plan
        plan = Plan(goal="Test Social Plan", steps=[])
        self.plan_id = self.state_manager.create_plan(plan)
        
        # 2. Create Task (We need a task ID for the post)
        # Manually inserting task via StateManager private method logic or custom SQL 
        # because create_plan usually inserts tasks too. 
        # But here plan.steps is empty. Let's insert a dummy task manually.
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO tasks (plan_id, step_index, description, assigned_agent, status) VALUES (?, 1, 'Test Social Task', 'social', 'in_progress')", (self.plan_id,))
        self.task_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # 3. Create Persona in DB (ID must match what we use in test)
        # We want ID=1. Auto-increment starts at 1 usually.
        conn.execute("INSERT INTO social_personas (name, handle, platform, description) VALUES ('Test Bot', 'test_user', 'twitter', 'Test styles')")
        self.persona_db_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()

        # Mock Personas Config
        # IMPORTANT: The ID key in this dict must match the DB ID (as string) 
        # because our Publisher uses `assigned_persona_id` from DB to look up config.
        self.test_persona = SocialPersona(
            id=str(self.persona_db_id),
            handle="test_user",
            style="Friendly",
            credentials={
                "twitter": {
                    "api_key": "mock_key",
                    "api_secret": "mock_secret",
                    "access_token": "mock_token", 
                    "access_token_secret": "mock_token_secret"
                },
                "reddit": {
                    "client_id": "mock_id",
                    "client_secret": "mock_secret",
                    "username": "test_user",
                    "password": "mock_password",
                    "user_agent": "mock_agent"
                },
                "bluesky": {
                    "handle": "mock_handle.bsky.social",
                    "app_password": "mock_password"
                },
                "substack": {
                    "email": "test@example.com",
                    "password": "mock_password",
                    "publication_url": "https://test.substack.com"
                }
            }
        )
        self.publisher.personas = {str(self.persona_db_id): self.test_persona}

    def tearDown(self):
        # Allow cleanup only if file is free
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                print(f"Warning: Could not delete {self.db_path} - file in use.")

    def test_draft_creation(self):
        # Test drafting a post
        # Pass the ID as string (Config ID) which matches DB ID
        result = self.publisher.post_update(
            platform="twitter",
            content="Hello World",
            persona_id=str(self.persona_db_id)
        )
        
        # Verify DB Draft
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM social_posts WHERE content = 'Hello World'")
        post = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(post, "Post should exist in DB")
        # Check return message specifically
        self.assertIn("PENDING USER APPROVAL", result)
        self.assertEqual(post[5], 'draft') # status column index 5
        self.assertEqual(post[4], 'twitter')

    @patch('tweepy.Client')
    def test_publish_twitter(self, MockTweepy):
        # 1. Create Draft
        self.publisher.post_update("twitter", "Hello Twitter", str(self.persona_db_id))
        
        # Get Post ID
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM social_posts LIMIT 1")
        post_id = cursor.fetchone()[0]
        conn.close()
        
        # 2. Mock API Response
        mock_client = MockTweepy.return_value
        mock_response = MagicMock()
        mock_response.data = {'id': '123456789'}
        mock_client.create_tweet.return_value = mock_response
        
        # 3. Publish
        result = self.publisher.publish_pending_post(post_id)
        
        # 4. Verify
        self.assertIn("Successfully published", result)
        mock_client.create_tweet.assert_called_with(text="Hello Twitter")
        
        # Verify DB Status Updated
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status, metrics FROM social_posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertEqual(row[0], 'published')
        self.assertIn('123456789', row[1])

    @patch('praw.Reddit')
    def test_publish_reddit(self, MockReddit):
        # 1. Create Draft
        self.publisher.post_update("reddit", "Title | Body Content", str(self.persona_db_id))
        
        # Get Post ID
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM social_posts WHERE platform='reddit' LIMIT 1")
        post_id = cursor.fetchone()[0]
        conn.close()

        # 2. Mock API
        mock_reddit_instance = MockReddit.return_value
        mock_subreddit = MagicMock()
        mock_submission = MagicMock()
        mock_submission.id = "red123"
        mock_submission.url = "http://reddit.com/r/test/red123"
        mock_subreddit.submit.return_value = mock_submission
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        
        # 3. Publish
        result = self.publisher.publish_pending_post(post_id)
        
        # 4. Verify
        self.assertIn("Successfully published", result)
        mock_subreddit.submit.assert_called()
        
        # Verify DB Status
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM social_posts WHERE id = ?", (post_id,))
        status = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(status, 'published')

    @patch('atproto.Client')
    def test_publish_bluesky(self, MockAtProto):
        # 1. Create Draft
        self.publisher.post_update("bluesky", "Hello Bluesky", str(self.persona_db_id))
        
        # Get Post ID (assuming previous tests left data, so query specifically)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM social_posts WHERE platform='bluesky' ORDER BY id DESC LIMIT 1")
        post_id = cursor.fetchone()[0]
        conn.close()

        # 2. Mock API
        mock_client = MockAtProto.return_value
        mock_post = MagicMock()
        mock_post.cid = "bafy..."
        mock_post.uri = "at://did:plc:123/app.bsky.feed.post/456"
        mock_client.send_post.return_value = mock_post
        
        # 3. Publish
        result = self.publisher.publish_pending_post(post_id)
        
        # 4. Verify
        self.assertIn("Successfully published", result)
        mock_client.login.assert_called_with("mock_handle.bsky.social", "mock_password")
        mock_client.send_post.assert_called_with(text="Hello Bluesky")

    @patch('substack.Api')
    def test_publish_substack(self, MockSubstackApi):
        # 1. Creating Draft (Post Update) - MOCKED remote call
        mock_api = MockSubstackApi.return_value
        mock_draft = MagicMock()
        mock_draft.id = "draft_789"
        mock_draft.draft_url = "https://test.substack.com/p/draft-789"
        mock_api.post_draft.return_value = mock_draft
        
        result_draft = self.publisher.post_update("substack", "Title | Body", str(self.persona_db_id))
        
        self.assertIn("Remote Draft created", result_draft)
        mock_api.post_draft.assert_called_with(title="Title", body="Body")

        # Get Post ID
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, metrics FROM social_posts WHERE platform='substack' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        post_id = row[0]
        metrics = row[1]
        conn.close()
        
        self.assertIn("draft_789", metrics)

        # 2. Publish
        mock_post = MagicMock()
        mock_post.id = "post_101"
        mock_post.url = "https://test.substack.com/p/published-post"
        mock_api.publish_draft.return_value = mock_post
        
        result_pub = self.publisher.publish_pending_post(post_id)
        
        # 3. Verify
        self.assertIn("Successfully published", result_pub)
        mock_api.publish_draft.assert_called_with("draft_789")

if __name__ == '__main__':
    # Need to import sqlite3 inside methods or globally
    import sqlite3
    unittest.main()
