
from agno.tools import Toolkit
from src.tools.browser import BrowserTools

class SocialTools(Toolkit):
    def __init__(self):
        super().__init__(name="social_tools")
        self.browser_tools = BrowserTools()
        self.register(self.social_login)
        self.register(self.post_update)
        self.register(self.monitor_topic)

    def social_login(self, platform: str) -> str:
        """
        Simulates logging into a social media platform.
        STUB with security warning.
        """
        warning = (
            f"WARNING: SECURITY RISK. Attempting to login to {platform}. "
            "In a real environment, use OAuth tokens or secure API keys. "
            "NEVER store passwords in plain text or pass them to the agent."
        )
        print(f"  [SocialTool] {warning}")
        return f"Successfully logged in to {platform} (STUB). {warning}"

    def post_update(self, platform: str, content: str) -> str:
        """
        Drafts a post for the specified platform.
        """
        # In this secure-by-design agent, we only DRAFT.
        print(f"  [SocialTool] Drafting post for {platform}: {content[:50]}...")
        return f"[DRAFT Created] for {platform}:\nContent: {content}\nStatus: PENDING USER APPROVAL."

    def monitor_topic(self, topic: str, platform: str) -> str:
        """
        Searches for recent discussions on a topic to gauge sentiment ('Vibe Check').
        """
        print(f"  [SocialTool] Monitoring sentiment for '{topic}' on {platform}...")
        
        # Reuse existing browser logic
        # Optimize query for sentiment/discussions
        search_query = f"site:{platform}.com {topic} discussion sentiment"
        
        # Call the browser tool directly
        # Note: calling the method directly on the instance
        results = self.browser_tools.search_web(search_query)
        
        return f"Recent sentiment scan for '{topic}' on {platform}:\n{results}"
