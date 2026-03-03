import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agno.agent import Agent
from agno.models.google import Gemini
from src.core.models import GEMINI_MODEL_ID
from src.tools.google_docs import GoogleDocsTools

# Add workspace/tarot to path so we can import the library
# Assuming the agent is running from the project root
WORKSPACE_DIR = Path("workspace/tarot")
sys.path.append(str(WORKSPACE_DIR.absolute()))

try:
    from deck import Deck
    from reading import Reading
    from spread import Spread
except ImportError:
    # Fallback if paths are tricky or running from different context
    # This might fail layout if not careful, but sticking to plan
    print("Warning: Could not import tarot library directly. TarotAgent features may be limited.")

class TarotAgent(Agent):
    def __init__(self, name: str = "MysticVibe", model_id: str = GEMINI_MODEL_ID):
        super().__init__(
            model=Gemini(id=model_id),
            description="A clinical and deeply authentic Tarot and Astrology diagnostics agent.",
            instructions=[
                "You are an expert Tarot Reader and Astrologer who speaks with strict clinical authenticity.",
                "ZERO SUGARCOATING CONSTRAINT: Eliminate all forced positivity. If critical, high-friction, or objective warnings emerge, report them with absolute honesty.",
                "Balance your diagnostics for reality, not comfort.",
                "When an astrology and tarot report is requested, your output must isolate into four explicit nodes:",
                "  1. Executive Summary",
                "  2. Astrology Diagnostic",
                "  3. Tarot Diagnostic",
                "  4. Actionable Mitigation Strategies (paired with any warnings or difficult transits)",
                "When a user asks for a reading, use the `perform_reading` tool to get the cards.",
                "CRITICAL: You MUST explicitly list the raw cards drawn along with their positions before providing the narrative synthesis.",
                "Do NOT drop the variables. Integrate them directly into the 'Tarot Diagnostic' node.",
                "IMPORTANT: When instructed to output to Google Docs, use the `post_to_google_doc` tool after generating your response.",
                "Ensure the title meets the exact format requested, e.g., 'YYYY-MM-DD: [first name] - Daily Astrology & Tarot Report'."
            ],
            tools=[self.perform_reading, GoogleDocsTools()]
        )

    def perform_reading(self, spread_type: str = "celtic_cross", question: str = "General diagnostic") -> str:
        """
        Perform a tarot reading using the internal card deck.
        
        Args:
            spread_type: The type of spread to use. Options: 'past_present_future', 'celtic_cross', 'horseshoe', 'relationship', 'career', 'daily_vibe' (maps to 'weekly' or 'single').
            question: The specific question to focus the reading on.
        """
        try:
            # Re-initialize deck for fresh shuffle
            deck = Deck()
            deck.shuffle_deck()
            reading_engine = Reading(deck)
            
            # Map simplified spread names if needed, or pass through
            # The existing library has many spreads. Let's try to match or default.
            if spread_type not in reading_engine.spreads:
                # Fallback to simple 3 card spread if unknown
                spread_type = "past_present_future"
                
            spread_obj = reading_engine.spreads[spread_type]
            spread_obj.draw_cards(deck)
            
            # Construct a structured string to return to the LLM
            # We don't want to just print it, we want to return data
            result = f"Spread: {spread_type}\n"
            result += f"Question: {question}\n\n"
            result += "Cards Drawn:\n"
            
            for position, card in spread_obj.cards.items():
                status = "Upright" if card.is_upright else "Reversed"
                result += f"- {position}: {card.name} ({status})\n"
                result += f"  Meaning Hints: {card.element}, {card.astrology}, {card.kabbalah}\n"
                
            result += f"\nElemental Dignities: {spread_obj.elemental_dignity()}\n"
            
            return result
            
        except Exception as e:
            return f"Error performing reading: {str(e)}"


if __name__ == "__main__":
    # Test execution
    agent = TarotAgent()
    print(agent.run("Give me a vibe check on my career"))
