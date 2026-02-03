import os
import unittest
import sys

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import load_social_personas
from src.agents.social import get_social_agent
from src.tools.social import SocialTools

class TestPersonaLoader(unittest.TestCase):
    def setUp(self):
        # Set up environment variables for testing
        os.environ["TWITTER_BOT_1_HANDLE"] = "@test_bot_1"
        os.environ["TWITTER_BOT_1_API_KEY"] = "secret_key_1"
        os.environ["TWITTER_BOT_1_STYLE_PROMPT"] = "Edgy and sarcastic."
        
        os.environ["TWITTER_BOT_2_HANDLE"] = "@test_bot_2"
        os.environ["TWITTER_BOT_2_API_KEY"] = "secret_key_2"
        # Bot 2 uses default style
        
        # Incomplete bot (should be ignored or warned)
        os.environ["TWITTER_BOT_3_HANDLE"] = "@test_bot_3"

    def tearDown(self):
        # Clean up env vars
        keys = [
            "TWITTER_BOT_1_HANDLE", "TWITTER_BOT_1_API_KEY", "TWITTER_BOT_1_STYLE_PROMPT",
            "TWITTER_BOT_2_HANDLE", "TWITTER_BOT_2_API_KEY",
            "TWITTER_BOT_3_HANDLE"
        ]
        for key in keys:
            if key in os.environ:
                del os.environ[key]

    def test_load_personas(self):
        personas = load_social_personas()
        
        # Verify Bot 1
        self.assertIn("1", personas)
        p1 = personas["1"]
        self.assertEqual(p1.handle, "@test_bot_1")
        self.assertEqual(p1.api_key, "secret_key_1")
        self.assertEqual(p1.style, "Edgy and sarcastic.")
        
        # Verify Bot 2
        self.assertIn("2", personas)
        p2 = personas["2"]
        self.assertEqual(p2.handle, "@test_bot_2")
        self.assertEqual(p2.style, "Standard professional tone.") # Default
        
        # Verify Bot 3 (incomplete) is NOT loaded
        self.assertNotIn("3", personas)

    def test_agent_instructions(self):
        agent = get_social_agent()
        instructions = "\n".join(agent.instructions)
        
        self.assertIn("AVAILABLE PERSONAS:", instructions)
        self.assertIn("ID: 1 | Handle: @test_bot_1 | Style: Edgy and sarcastic.", instructions)
        self.assertIn("ID: 2 | Handle: @test_bot_2", instructions)

    def test_tool_usage_simulation(self):
        # Verify tool can lookup credentials
        tools = SocialTools()
        # Mock the personas dict directly since we modify env vars in setUp
        tools.personas = load_social_personas() 
        
        # We can't easily assert print output here without redirecting stdout, 
        # but we can call the method and ensure it doesn't crash
        result = tools.post_update("twitter", "Hello", persona_id="1")
        self.assertIn("PENDING USER APPROVAL", result)
        self.assertIn("@test_bot_1", result)

if __name__ == "__main__":
    unittest.main()
