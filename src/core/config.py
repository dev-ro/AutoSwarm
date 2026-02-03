
import os
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class SocialPersona:
    """
    Represents a loaded social media persona configuration.
    Credentials are meant to be used by safe tools, not directly by the LLM.
    """
    id: str  # Internal ID, e.g. "BOT_1"
    handle: str
    style: str
    # Flexible credentials storage: platform -> {key: value}
    # e.g. {'twitter': {'api_key': '...', 'api_secret': '...'}, 'reddit': {...}}
    credentials: Dict[str, Dict[str, str]] = field(default_factory=dict)

def load_social_personas() -> Dict[str, SocialPersona]:
    """
    Parses environment variables to load social personas.
    Expects vars like:
    TWITTER_BOT_{ID}_HANDLE
    TWITTER_BOT_{ID}_API_KEY
    TWITTER_BOT_{ID}_API_SECRET
    TWITTER_BOT_{ID}_ACCESS_TOKEN
    TWITTER_BOT_{ID}_ACCESS_TOKEN_SECRET
    
    REDDIT_BOT_{ID}_CLIENT_ID
    REDDIT_BOT_{ID}_CLIENT_SECRET
    
    Returns a dictionary keyed by the persona ID (e.g., "1").
    """
    personas: Dict[str, SocialPersona] = {}
    
    # Regex to capture the ID from the variable name
    # We scan specifically for handles to identify active bots
    pattern = re.compile(r"(TWITTER|REDDIT|FACEBOOK|LINKEDIN)_BOT_(\w+)_HANDLE")
    
    for key, value in os.environ.items():
        match = pattern.match(key)
        if match:
            platform_prefix = match.group(1) # TWITTER, REDDIT, etc.
            bot_id = match.group(2)
            
            # Check if we already started building this persona
            if bot_id not in personas:
                # Initialize with a basic handle (Twitter's usually serves as main ID)
                # We'll refine the style prompt from the first one we find
                base_style_key = f"{platform_prefix}_BOT_{bot_id}_STYLE_PROMPT"
                style = os.environ.get(base_style_key, "Standard professional tone.")
                
                personas[bot_id] = SocialPersona(
                    id=bot_id,
                    handle=value, # Primary handle found
                    style=style,
                    credentials={}
                )
            
            # Load credentials for this platform
            base = f"{platform_prefix}_BOT_{bot_id}"
            creds = {}
            
            if platform_prefix == "TWITTER":
                creds = {
                    "api_key": os.environ.get(f"{base}_API_KEY", ""),
                    "api_secret": os.environ.get(f"{base}_API_SECRET", ""),
                    "access_token": os.environ.get(f"{base}_ACCESS_TOKEN", ""),
                    "access_token_secret": os.environ.get(f"{base}_ACCESS_TOKEN_SECRET", ""),
                    "bearer_token": os.environ.get(f"{base}_BEARER_TOKEN", "")
                }
            elif platform_prefix == "REDDIT":
                creds = {
                    "client_id": os.environ.get(f"{base}_CLIENT_ID", ""),
                    "client_secret": os.environ.get(f"{base}_CLIENT_SECRET", ""),
                    "user_agent": os.environ.get(f"{base}_USER_AGENT", "AutoSwarmBot/1.0"),
                    "username": os.environ.get(f"{base}_USERNAME", ""),
                    "password": os.environ.get(f"{base}_PASSWORD", "")
                }
            elif platform_prefix == "FACEBOOK":
                creds = {
                    "page_id": os.environ.get(f"{base}_PAGE_ID", ""),
                    "page_access_token": os.environ.get(f"{base}_PAGE_ACCESS_TOKEN", "")
                }
            elif platform_prefix == "LINKEDIN":
                creds = {
                    "urn": os.environ.get(f"{base}_URN", ""), # e.g., urn:li:person:123
                    "access_token": os.environ.get(f"{base}_ACCESS_TOKEN", "")
                }
            elif platform_prefix == "BLUESKY":
                creds = {
                    "handle": os.environ.get(f"{base}_HANDLE", ""),
                    "app_password": os.environ.get(f"{base}_APP_PASSWORD", "")
                }
            elif platform_prefix == "SUBSTACK":
                creds = {
                    "email": os.environ.get(f"{base}_EMAIL", ""),
                    "password": os.environ.get(f"{base}_PASSWORD", ""),
                    "publication_url": os.environ.get(f"{base}_PUBLICATION_URL", "")
                }

            # Filter out empty keys
            creds = {k: v for k, v in creds.items() if v}
            
            # Store in the persona credentials dict under the platform name (lowercase)
            personas[bot_id].credentials[platform_prefix.lower()] = creds
            print(f"[Config] Loaded {platform_prefix.lower()} credentials for persona {bot_id}")

    return personas
