import json
import requests
import tweepy
import praw
from typing import Optional, Dict, Any
from agno.tools import Toolkit
from src.core.config import load_social_personas
from src.core.state import StateManager

class SocialPublisher(Toolkit):
    def __init__(self, state_manager: StateManager):
        super().__init__(name="social_publisher")
        self.state = state_manager
        self.personas = load_social_personas()
        
        # Register tools available to the Agent
        self.register(self.post_update)
        self.register(self.publish_pending_post) # For explicit "execute" commands if needed, or mostly via system loop

    def post_update(self, platform: str, content: str, persona_id: str) -> str:
        """
        SAFE MODE: Drafts a post for the specified platform.
        Does NOT publish immediately.
        
        :param platform: The platform to post to (twitter, reddit, facebook, linkedin, bluesky, substack)
        :param content: The content of the post
        :param persona_id: The ID of the persona to use
        """
        print(f"  [SocialPublisher] Drafting post for {platform} as persona {persona_id}...")
        
        # valid platform check
        platform = platform.lower()
        if platform not in ["twitter", "reddit", "facebook", "linkedin", "bluesky", "substack"]:
            return f"Error: Unsupported platform '{platform}'."

        # Verify persona
        persona = self.personas.get(persona_id)
        if not persona:
            return f"Error: Persona ID '{persona_id}' not found."

        # Substack Special Handling: Create Draft on Platform
        remote_metadata = {}
        if platform == 'substack':
            try:
                creds = persona.credentials.get('substack')
                if not creds:
                     return "Error: No Substack credentials found for this persona."
                # Call internal helper to create draft
                remote_metadata = self._draft_substack(content, creds)
            except Exception as e:
                return f"Error: Failed to create Substack draft. {e}"

        # Create Post in DB (Draft)
        active_plan = self.state.get_active_plan()
        task_id = 0
        if active_plan:
             for t in active_plan['tasks']:
                 if t['status'] == 'in_progress':
                     task_id = t['id']
                     break
        
        # We store remote_metadata (e.g. draft_id) in metrics for now as initial state
        post_id = self.state.create_post(
            task_id=task_id if task_id else 1, 
            content=content,
            platform=platform,
            assigned_persona_id=int(persona_id) if persona_id.isdigit() else None
        )
        
        if remote_metadata:
             self.state.update_post_status(post_id, "draft", remote_metadata)

        if post_id == -1:
            return "Error: Failed to save draft to database."

        msg = f"PENDING USER APPROVAL (Draft ID: {post_id}). Content saved for {platform}."
        if platform == 'substack':
            msg += f" (Remote Draft created: ID {remote_metadata.get('draft_id')})"
        return msg

    def publish_pending_post(self, post_id: int) -> str:
        """
        EXECUTION MODE: Publishes a draft post after human approval.
        """
        # 1. Retrieve Post
        import sqlite3
        conn = sqlite3.connect(self.state.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM social_posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        conn.close()

        if not post:
            return f"Error: Post {post_id} not found."
        
        if post['status'] == 'published':
            return f"Post {post_id} is already published."

        # 2. Retrieve Persona and Credentials
        persona_id_db = post['assigned_persona_id']
        persona_conf = self.personas.get(str(persona_id_db))
        if not persona_conf:
             return f"Error: configuration for persona ID {persona_id_db} not found."

        platform = post['platform']
        creds = persona_conf.credentials.get(platform)
        
        if not creds:
             self.state.update_post_status(post_id, "failed", {"error": f"No credentials for {platform}"})
             return f"Error: No credentials found for {platform} on persona {persona_conf.handle}."

        # 3. Publish
        try:
            result_metrics = {}
            # Parse existing metrics (which might contain draft_id for substack)
            current_metrics = json.loads(post['metrics']) if post['metrics'] else {}

            if platform == 'twitter':
                result_metrics = self._publish_twitter(post['content'], creds)
            elif platform == 'reddit':
                result_metrics = self._publish_reddit(post['content'], creds)
            elif platform == 'facebook':
                result_metrics = self._publish_facebook(post['content'], creds)
            elif platform == 'linkedin':
                result_metrics = self._publish_linkedin(post['content'], creds)
            elif platform == 'bluesky':
                result_metrics = self._publish_bluesky(post['content'], creds)
            elif platform == 'substack':
                result_metrics = self._publish_substack(post['content'], creds, current_metrics)
            else:
                raise ValueError(f"Unknown platform {platform}")

            # Success
            self.state.update_post_status(post_id, "published", result_metrics)
            return f"Successfully published to {platform}. Metrics: {result_metrics}"

        except Exception as e:
            error_msg = str(e)
            print(f"[SocialPublisher] Publish failed: {error_msg}")
            self.state.update_post_status(post_id, "failed", {"error": error_msg})
            return f"Error: Publishing failed. {error_msg}"

    # --- Platform Implementations ---

    def _publish_twitter(self, content: str, creds: Dict) -> Dict:
        """Publishes to Twitter using Tweepy."""
        client = tweepy.Client(
            consumer_key=creds['api_key'],
            consumer_secret=creds['api_secret'],
            access_token=creds['access_token'],
            access_token_secret=creds['access_token_secret'],
            bearer_token=creds.get('bearer_token')
        )
        response = client.create_tweet(text=content)
        return {"tweet_id": response.data['id']}

    def _publish_reddit(self, content: str, creds: Dict) -> Dict:
        """Publishes to Reddit using PRAW."""
        reddit = praw.Reddit(
            client_id=creds['client_id'],
            client_secret=creds['client_secret'],
            user_agent=creds['user_agent'],
            username=creds['username'],
            password=creds['password']
        )
        # Assuming content formatting: "Title | Body" or just Body if no pipe
        if "|" in content:
            title, body = content.split("|", 1)
        else:
            title = content[:100] # Truncate for title
            body = content
        
        # Need a target subreddit. This should ideally be in prompt or config.
        # Defaulting to a safe test one or from config if exists
        subreddit_name = creds.get('default_subreddit', 'u_' + creds['username']) 
        
        submission = reddit.subreddit(subreddit_name).submit(title=title.strip(), selftext=body.strip())
        return {"submission_id": submission.id, "url": submission.url}

    def _publish_facebook(self, content: str, creds: Dict) -> Dict:
        """Publishes to Facebook Page."""
        page_id = creds['page_id']
        token = creds['page_access_token']
        url = f"https://graph.facebook.com/{page_id}/feed"
        payload = {'message': content, 'access_token': token}
        
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"post_id": data['id']}

    def _publish_linkedin(self, content: str, creds: Dict) -> Dict:
        """Publishes to LinkedIn UGC API."""
        author_urn = creds['urn']
        access_token = creds['access_token']
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        resp = requests.post(url, headers=headers, json=post_data, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"urn": data['id']}

    def _publish_bluesky(self, content: str, creds: Dict) -> Dict:
        """Publishes to Bluesky using atproto."""
        try:
            from atproto import Client
        except ImportError:
            raise ImportError("atproto library not installed.")

        client = Client()
        client.login(creds['handle'], creds['app_password'])
        post = client.send_post(text=content)
        # Handle facets (mentions/links) is automatic in newer atproto versions usually, 
        # or requires explicit processing. User asked for automatic if possible.
        # send_post handles basic text.
        return {"cid": post.cid, "uri": post.uri}

    def _draft_substack(self, content: str, creds: Dict) -> Dict:
        """
        Creates a draft on Substack dashboard.
        Returns metadata including draft_id.
        """
        try:
            import substack
        except ImportError:
            raise ImportError("python-substack library not installed.")

        # Note: API methods are assumed based on library wrapper convention
        api = substack.Api(
            email=creds['email'],
            password=creds['password'],
            publication_url=creds['publication_url']
        )
        
        # content parsing: Title | Body
        if "|" in content:
            title, body = content.split("|", 1)
        else:
            title = "Agent Draft"
            body = content
            
        draft = api.post_draft(title=title.strip(), body=body.strip())
        # Assuming draft object has 'id' attribute
        return {"draft_id": draft.id, "url": draft.draft_url}

    def _publish_substack(self, content: str, creds: Dict, metrics: Dict = {}) -> Dict:
        """
        Publishes a Substack draft using the draft_id from metrics.
        """
        try:
            import substack
        except ImportError:
            raise ImportError("python-substack library not installed.")
            
        api = substack.Api(
            email=creds['email'],
            password=creds['password'],
            publication_url=creds['publication_url']
        )
        
        draft_id = metrics.get('draft_id')
        if not draft_id:
             raise ValueError("Cannot publish Substack post: Missing 'draft_id' in metrics. Was the draft created successfully?")

        post = api.publish_draft(draft_id)
        return {"post_id": post.id, "url": post.url}

