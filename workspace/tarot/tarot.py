from deck import Deck
from reading import Reading

def main():
    deck = Deck()
    reading = Reading(deck)

    # Perform a few sample readings with upright cards only
    # sample_spreads = ["past_present_future", "celtic_cross", "horseshoe"]
    # print(deck.print_deck_description())
    n = len(reading.spreads)
    for i, spread_name in enumerate(reading.spreads):
        # do half of the spreads
        if i == n//2:
            input("Press Enter to continue...")

        # print(f"Performing '{spread_name}' reading with upright cards only:")
        # print(deck.print_deck_description())
        reading.perform_reading(spread_name, upright_only=False)
        print("="*100)
        print()

if __name__ == "__main__":
    main()
