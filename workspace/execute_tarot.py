import sys
import os
import json

# Add current directory to path so we can import 'tarot'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from tarot.deck import Deck
    from tarot.reading import Reading
    from tarot.card import Card
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def main():
    deck = Deck()
    deck.shuffle_deck()
    
    # 1. Capture raw output of a single card draw
    print("--- SINGLE CARD DRAW ---")
    card = deck.draw_card()
    print(f"Card Name: {card.name}")
    print(f"Upright: {card.is_upright}")
    print(f"Metadata: {json.dumps(card.to_dict(), indent=2)}")
    print(f"String representation: {card}")
    print("\n")

    # 2. Capture raw output of a full spread
    print("--- FULL SPREAD (past_present_future) ---")
    reading = Reading(deck)
    spread_name = "past_present_future"
    spread = reading.spreads[spread_name]
    
    # We need to shuffle again because drawing one card removed it from the shuffled deck
    deck.shuffle_deck()
    spread.draw_cards(deck)
    
    # Display the spread (standard output)
    spread.display()
    
    # Get analysis data
    analysis_data = spread.get_analysis_data()
    print("--- ANALYSIS DATA (JSON) ---")
    print(json.dumps(analysis_data, indent=2))

if __name__ == "__main__":
    main()