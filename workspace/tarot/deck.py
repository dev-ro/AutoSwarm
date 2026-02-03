import random
from card import Card


class Deck:
    DECKS = {
        "Rider-Waite-Smith": {
            "name": "Rider-Waite-Smith",
            "imagery": "Detailed, symbolic imagery for all cards, including the Minor Arcana.",
            "symbolism": "Rich in esoteric symbols from various traditions.",
            "use": "Widely used for both learning and professional readings.",
        },
        "Thoth": {
            "name": "Thoth",
            "imagery": "Abstract and complex artwork.",
            "symbolism": "Incorporates elements from astrology, Kabbalah, and alchemy.",
            "use": "Preferred by those interested in esoteric and occult traditions.",
        },
        "Tarot de Marseille": {
            "name": "Tarot de Marseille",
            "imagery": "Simple, woodcut-style illustrations.",
            "symbolism": "Rooted in historical European traditions, with a focus on numerology.",
            "use": "Favored for traditional readings and historical approach.",
        },
        "The Wild Unknown": {
            "name": "The Wild Unknown",
            "imagery": "Hand-drawn black-and-white illustrations with bursts of color, focusing on animals and nature.",
            "symbolism": "Simplified yet profound, using animals and natural elements.",
            "use": "Popular for its intuitive, earthy feel and modern aesthetic.",
        },
        "Shadowscapes": {
            "name": "Shadowscapes",
            "imagery": "Detailed, watercolor artwork with a fantasy theme.",
            "symbolism": "Rich in mythological and fantastical elements.",
            "use": "Favored by those who enjoy elaborate and whimsical imagery.",
        },
        "Modern Witch Tarot": {
            "name": "Modern Witch Tarot",
            "imagery": "Contemporary, vibrant illustrations featuring diverse characters and modern settings.",
            "symbolism": "Stays true to traditional RWS symbolism with modern updates.",
            "use": "Popular for its inclusivity and modern representation.",
        },
        "The Light Seer's Tarot": {
            "name": "The Light Seer's Tarot",
            "imagery": "Bright, colorful illustrations with a focus on positivity and light.",
            "symbolism": "Combines traditional tarot symbols with modern interpretations.",
            "use": "Ideal for those seeking an encouraging and positive reading experience.",
        },
        "The Starchild Tarot": {
            "name": "The Starchild Tarot",
            "imagery": "Ethereal, cosmic artwork with a mix of digital and hand-drawn elements.",
            "symbolism": "Integrates spiritual and metaphysical themes.",
            "use": "Favored by those interested in spiritual and cosmic insights.",
        },
        "The Prisma Visions Tarot": {
            "name": "The Prisma Visions Tarot",
            "imagery": "Impressionistic, colorful artwork that creates a continuous narrative.",
            "symbolism": "Artistic and imaginative, blending traditional and contemporary symbolism.",
            "use": "Great for creative and visually driven readings.",
        },
        "The Fountain Tarot": {
            "name": "The Fountain Tarot",
            "imagery": "Modern, minimalist design with a focus on clarity and elegance.",
            "symbolism": "Combines traditional elements with modern art sensibilities.",
            "use": "Preferred for its sleek, modern aesthetic and thoughtful symbolism.",
        },
    }

    def __init__(self, selected_deck="Rider-Waite-Smith"):
        self.selected_deck = selected_deck
        self.cards = self._initialize_deck()  # Initialize the deck with cards
        self.shuffled_deck = []  # List to hold shuffled cards

    def _initialize_deck(self):
        major_arcana = [
            ("The Fool", 0),
            ("The Magician", 1),
            ("The High Priestess", 2),
            ("The Empress", 3),
            ("The Emperor", 4),
            ("The Hierophant", 5),
            ("The Lovers", 6),
            ("The Chariot", 7),
            ("Strength", 8),
            ("The Hermit", 9),
            ("Wheel of Fortune", 10),
            ("Justice", 11),
            ("The Hanged Man", 12),
            ("Death", 13),
            ("Temperance", 14),
            ("The Devil", 15),
            ("The Tower", 16),
            ("The Star", 17),
            ("The Moon", 18),
            ("The Sun", 19),
            ("Judgement", 20),
            ("The World", 21),
        ]

        minor_arcana = (
            [(f"Ace of {suit}", 1) for suit in ["Wands", "Cups", "Swords", "Pentacles"]]
            + [
                (f"{rank} of {suit}", rank)
                for suit in ["Wands", "Cups", "Swords", "Pentacles"]
                for rank in range(2, 11)
            ]
            + [
                (f"Page of {suit}", 11)
                for suit in ["Wands", "Cups", "Swords", "Pentacles"]
            ]
            + [
                (f"Knight of {suit}", 12)
                for suit in ["Wands", "Cups", "Swords", "Pentacles"]
            ]
            + [
                (f"Queen of {suit}", 13)
                for suit in ["Wands", "Cups", "Swords", "Pentacles"]
            ]
            + [
                (f"King of {suit}", 14)
                for suit in ["Wands", "Cups", "Swords", "Pentacles"]
            ]
        )

        return major_arcana + minor_arcana

    def shuffle_deck(self, times=1111):
        """Shuffle the deck a specified number of times."""
        self.shuffled_deck = [Card(name, number, True) for name, number in self.cards]
        for _ in range(times):
            random.shuffle(self.shuffled_deck)

    def draw_card(self, upright_only=False):
        """Draw a card from the shuffled deck."""
        while self.shuffled_deck:
            card = self.shuffled_deck.pop(0)
            card.is_upright = random.choice([True, False])
            if upright_only and not card.is_upright:
                continue
            return card
        raise IndexError("The deck is empty. Please shuffle the deck first.")

    def print_deck_description(self):
        """Print the description of the selected deck."""
        description = self.DECKS.get(self.selected_deck, {})
        if description:
            return f"Deck Name: {description['name']} \nImagery: {description['imagery']} \nSymbolism: {description['symbolism']} \nUse: {description['use']}\n"
        else:
            return "Deck description not found."
