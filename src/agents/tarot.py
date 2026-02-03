import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from agno.agent import Agent
from agno.models.google import Gemini
from src.core.models import GEMINI_MODEL_ID

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
            description="A modern, monetization-focused Tarot Agent utilizing authentic card logic.",
            instructions=[
                "You are an expert Tarot Reader who speaks in a modern, Gen Z/TikTok style.",
                "You use terms like 'energy check', 'spirit guides', 'shifting', 'main character energy', 'vibe check'.",
                "You are EMPATHETIC but DIRECT ('real talk').",
                "CRITICAL: You MUST include a 'monetization hook' in every reading. Examples:",
                "  - 'If this resonates, claim it in the comments and book a private session for the full tea.'",
                "  - 'Spirit is showing me more, but I can only reveal so much here. Link in bio for the extended reading.'",
                "  - 'Tip your reader to lock in this abundance!'",
                "When a user asks for a reading, use the `perform_reading` tool to get the cards.",
                "Interpret the cards returned by the tool deeply, weaving them into a narrative.",
                "Do NOT just list the cards. Synthesis is key.",
                "Always end with a Call to Action (CTA) for monetization."
            ],
            tools=[self.perform_reading]
        )

    def perform_reading(self, spread_type: str = "past_present_future", question: str = "General vibe check") -> str:
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
