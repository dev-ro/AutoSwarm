import os
from agno.models.google import Gemini

# Default configuration
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-3-flash-preview")

def get_executive_model():
    """
    Returns a configured Gemini model instance.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[WARNING] GOOGLE_API_KEY not found. Agent initialization may fail.")
    
    return Gemini(
        id=GEMINI_MODEL_ID,
        api_key=api_key
    )
