import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.google_docs import GoogleDocsTools

from src.tarot.deck import Deck
from src.tarot.reading import Reading
from src.tarot.spread import Spread

class TarotAgent(Agent):
    def __init__(self, name: str = "MysticVibe"):
        super().__init__(
            model=get_executive_model(),
            description="A clinical and deeply authentic Tarot and Astrology diagnostics agent.",
            instructions=[
                "You are an expert Tarot Reader and Astrologer functioning as a diagnostic engine.",
                "MAXIMUM SIGNAL DENSITY MANDATE: Output must strictly contain high-value, direct, actionable insights. Eliminate ALL conversational filler, platitudes, and forced positivity.",
                "ZERO SUGARCOATING CONSTRAINT: If critical, high-friction, or objective warnings emerge, report them with absolute clinical honesty.",
                "PROMPT ARCHITECTURE (SECOND PERSON): Address the user directly ('you').",
                "Your output must isolate into four explicit nodes:",
                "1. Executive Summary: Declarative 2-3 sentence overview of the current state.",
                "2. Astrology Diagnostic (Technical transit analysis): Precise astrological correlations with no fluff.",
                "3. Tarot Diagnostic (Celtic Cross interpretation): Integration of raw card data into a synthesized structural assessment.",
                "4. Actionable Mitigation Strategies (Practical steps): Bulleted list of highly specific, implementable directives based on the diagnostics.",
                "When a user asks for a reading, you MUST use the `perform_reading` tool with spread_type='celtic_cross' unless explicitly told otherwise.",
                "CRITICAL: You MUST explicitly list the raw cards drawn along with their positions before providing the narrative synthesis.",
                "IMPORTANT: When instructed to output to Google Docs, use the `post_to_google_doc` tool after generating your response.",
                "Ensure the title meets the exact format requested, e.g., 'YYYY-MM-DD: [first name] - Daily Astrology & Tarot Report'."
            ],
            tools=[self.perform_reading, GoogleDocsTools()]
        )

    def perform_reading(self, spread_type: str = "celtic_cross", question: str = "General diagnostic") -> str:
        """
        Perform a tarot reading using the internal card deck.
        
        Args:
            spread_type: The type of spread to use. Options: 'past_present_future', 'celtic_cross', 'horseshoe', 'relationship', 'career', 'astrological', 'yearly', 'karmic', 'elemental', 'journey', 'healing', 'decision_making', 'spiritual_growth', 'new_beginnings', 'inner_conflict', 'financial_insight', 'personal_growth', 'life_purpose', 'life_path', 'elemental_balance', 'conflict_resolution', 'creativity', 'self_discovery', 'manifestation', 'change_and_transition', 'dream_interpretation', 'family_dynamics', 'spiritual_awakening', 'personal_power', 'relationship_potential', 'decision_clarifier', 'soul_purpose', 'love_and_relationship', 'clarity', 'empowerment', 'soulmate', 'intuition', 'weekly'.
            question: The specific question to focus the reading on.
        """
        # Re-initialize deck for fresh shuffle
        deck = Deck()
        deck.shuffle_deck()
        reading_engine = Reading(deck)
        
        try:
            # Validate spread type against reading engine
            if spread_type not in reading_engine.spreads:
                # Fallback to celtic_cross if unknown
                spread_type = "celtic_cross"
                
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
