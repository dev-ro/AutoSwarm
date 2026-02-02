
import os
from dotenv import load_dotenv
from agno.models.google import Gemini

load_dotenv()

# We use the Gemini 3 Pro Preview model as requested.
GEMINI_MODEL_ID = "gemini-3-pro-preview"

def get_executive_model():
    """
    Returns a configured Gemini model instance for the Executive Agent.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY not found in environment variables.")
    
    return Gemini(
        id=GEMINI_MODEL_ID,
        api_key=api_key
    )
