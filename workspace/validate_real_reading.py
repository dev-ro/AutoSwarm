import sys
import os
import json
from datetime import datetime

# Add the tarot directory to the path
sys.path.append(os.path.join(os.getcwd(), 'tarot'))

from deck import Deck
from reading import Reading
from tarot_schema import validate_reading_data

def test_real_data_validation():
    deck = Deck()
    reading = Reading(deck)
    spread_name = "celtic_cross"
    target_signs = ["Sagittarius", "Capricorn"]
    persona = "main_character"
    
    spread = reading.spreads[spread_name]
    deck.shuffle_deck()
    spread.draw_cards(deck)
    
    # Get structured data
    analysis_data = spread.get_analysis_data(target_signs=target_signs, persona=persona)
    
    # Construct the full reading object for the knowledge base
    reading_record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "spread": spread_name,
        "persona": persona,
        "cards": analysis_data["cards"],
        "synthesis": analysis_data["synthesis"]
    }
    
    knowledge_base = {
        "readings": [reading_record]
    }
    
    print("Generated Reading Data:")
    # print(json.dumps(knowledge_base, indent=2))
    
    try:
        validate_reading_data(knowledge_base)
        print("\nSUCCESS: Real reading data matches the designed schema.")
        
        # Save to a temporary file for validation
        with open("validated_reading.json", "w") as f:
            json.dump(knowledge_base, f, indent=2)
        print("Validated reading saved to validated_reading.json")
        
    except Exception as e:
        print(f"\nFAILURE: Real reading data does NOT match the schema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_real_data_validation()