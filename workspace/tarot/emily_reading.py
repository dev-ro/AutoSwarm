from deck import Deck
from reading import Reading

def perform_emily_reading():
    # Emily born Dec 20, 1986 -> Sagittarius-Capricorn Cusp
    # Date of reading: February 03, 2026
    
    print("SPIRITUAL GUIDANCE REPORT FOR EMILY")
    print("Date: February 03, 2026")
    print("Birth Date: December 20, 1986 (Sagittarius-Capricorn Cusp)")
    print("-" * 40)
    
    deck = Deck()
    reading = Reading(deck)
    
    # 10-card Celtic Cross spread
    reading.perform_reading("celtic_cross", target_signs=["Sagittarius", "Capricorn"])

if __name__ == "__main__":
    perform_emily_reading()