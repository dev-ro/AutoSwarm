import json
import os
import re
from pathlib import Path

class Card:
    _database = None

    astrological_correspondences = {
        "The Fool": "Uranus",
        "The Magician": "Mercury",
        "The High Priestess": "Moon",
        "The Empress": "Venus",
        "The Emperor": "Aries",
        "The Hierophant": "Taurus",
        "The Lovers": "Gemini",
        "The Chariot": "Cancer",
        "Strength": "Leo",
        "The Hermit": "Virgo",
        "Wheel of Fortune": "Jupiter",
        "Justice": "Libra",
        "The Hanged Man": "Neptune",
        "Death": "Scorpio",
        "Temperance": "Sagittarius",
        "The Devil": "Capricorn",
        "The Tower": "Mars",
        "The Star": "Aquarius",
        "The Moon": "Pisces",
        "The Sun": "Sun",
        "Judgement": "Pluto",
        "The World": "Saturn",
    }
    minor_arcana_correspondences = {
        "2 of Wands": "Mars in Aries",
        "3 of Wands": "Sun in Aries",
        "4 of Wands": "Venus in Aries",
        "5 of Wands": "Saturn in Leo",
        "6 of Wands": "Jupiter in Leo",
        "7 of Wands": "Mars in Leo",
        "8 of Wands": "Mercury in Sagittarius",
        "9 of Wands": "Moon in Sagittarius",
        "10 of Wands": "Saturn in Sagittarius",
        "2 of Cups": "Venus in Cancer",
        "3 of Cups": "Mercury in Cancer",
        "4 of Cups": "Moon in Cancer",
        "5 of Cups": "Mars in Scorpio",
        "6 of Cups": "Sun in Scorpio",
        "7 of Cups": "Venus in Scorpio",
        "8 of Cups": "Saturn in Pisces",
        "9 of Cups": "Jupiter in Pisces",
        "10 of Cups": "Mars in Pisces",
        "2 of Swords": "Moon in Libra",
        "3 of Swords": "Saturn in Libra",
        "4 of Swords": "Jupiter in Libra",
        "5 of Swords": "Venus in Aquarius",
        "6 of Swords": "Mercury in Aquarius",
        "7 of Swords": "Moon in Aquarius",
        "8 of Swords": "Jupiter in Gemini",
        "9 of Swords": "Mars in Gemini",
        "10 of Swords": "Sun in Gemini",
        "2 of Pentacles": "Jupiter in Capricorn",
        "3 of Pentacles": "Mars in Capricorn",
        "4 of Pentacles": "Sun in Capricorn",
        "5 of Pentacles": "Mercury in Taurus",
        "6 of Pentacles": "Moon in Taurus",
        "7 of Pentacles": "Saturn in Taurus",
        "8 of Pentacles": "Sun in Virgo",
        "9 of Pentacles": "Venus in Virgo",
        "10 of Pentacles": "Mercury in Virgo",
    }
    kabbalistic_correspondences = {
        "The Fool": "Aleph (Air)",
        "The Magician": "Beth (Mercury)",
        "The High Priestess": "Gimel (Moon)",
        "The Empress": "Daleth (Venus)",
        "The Emperor": "Heh (Aries)",
        "The Hierophant": "Vau (Taurus)",
        "The Lovers": "Zain (Gemini)",
        "The Chariot": "Cheth (Cancer)",
        "Strength": "Teth (Leo)",
        "The Hermit": "Yod (Virgo)",
        "Wheel of Fortune": "Kaph (Jupiter)",
        "Justice": "Lamed (Libra)",
        "The Hanged Man": "Mem (Water)",
        "Death": "Nun (Scorpio)",
        "Temperance": "Samekh (Sagittarius)",
        "The Devil": "Ayin (Capricorn)",
        "The Tower": "Peh (Mars)",
        "The Star": "Tzaddi (Aquarius)",
        "The Moon": "Qoph (Pisces)",
        "The Sun": "Resh (Sun)",
        "Judgement": "Shin (Fire)",
        "The World": "Tau (Saturn)",
    }
    major_elements = {
        "The Fool": "Air",
        "The Magician": "Air",
        "The High Priestess": "Water",
        "The Empress": "Earth",
        "The Emperor": "Fire",
        "The Hierophant": "Earth",
        "The Lovers": "Air",
        "The Chariot": "Water",
        "Strength": "Fire",
        "The Hermit": "Earth",
        "Wheel of Fortune": "Fire",
        "Justice": "Air",
        "The Hanged Man": "Water",
        "Death": "Water",
        "Temperance": "Fire",
        "The Devil": "Earth",
        "The Tower": "Fire",
        "The Star": "Air",
        "The Moon": "Water",
        "The Sun": "Fire",
        "Judgement": "Fire",
        "The World": "Earth",
    }

    def __init__(self, name, number, is_upright=True):
        self.name = name
        self.number = number
        self.is_upright = is_upright
        self.arcana = self.get_arcana()
        self.suit = self.get_suit()
        self.element = self.get_element()
        self.astrology = self.get_astrological_correspondence()
        self.kabbalah = self.get_kabbalistic_correspondence()
        self._load_database()

    def get_arcana(self):
        if any(suit in self.name for suit in ["Wands", "Cups", "Swords", "Pentacles"]):
            return "Minor"
        return "Major"

    def get_suit(self):
        for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
            if suit in self.name:
                return suit
        return "None"

    def _load_database(self):
        if Card._database is None:
            # Use absolute path relative to this file
            base_dir = Path(__file__).parent
            db_path = base_dir / "tarot_database.json"
            
            if db_path.exists():
                try:
                    with open(db_path, 'r', encoding='utf-8') as f:
                        Card._database = json.load(f)
                except Exception as e:
                    print(f"Error loading tarot database: {e}")
                    Card._database = {}
            else:
                # Fallback to current working directory or other common locations
                paths = [
                    Path("tarot/tarot_database.json"),
                    Path("tarot_database.json"),
                ]
                for path in paths:
                    if path.exists():
                        try:
                            with open(path, 'r', encoding='utf-8') as f:
                                Card._database = json.load(f)
                            return
                        except Exception:
                            continue
                Card._database = {}
    
    def _normalize(self, s):
        is_minor = any(suit in s for suit in ["Wands", "Cups", "Swords", "Pentacles"])
        if not is_minor:
            s = re.sub(r'^\d+[\.\s]+', '', s)
        s = s.replace('The ', '').strip().title()
        s = s.replace(' Of ', ' of ')
        return s

    def get_vibe_check(self, persona="main_character"):
        if not Card._database:
            return {"keywords": "Data not found", "narrative": "Data not found", "traditional": "Data not found"}
        
        norm_name = self._normalize(self.name)
        card_data = None
        
        # Try direct match or normalized match
        if norm_name in Card._database:
            card_data = Card._database[norm_name]
        else:
            for key in Card._database:
                if self._normalize(key) == norm_name:
                    card_data = Card._database[key]
                    break
        
        if not card_data:
            return {
                "keywords": "Narrative not available", 
                "narrative": f"Modern narrative not available for {self.name}",
                "traditional": "Traditional meaning not available."
            }
        
        personas = card_data.get("personas", {})
        # Get selected persona or default to main_character
        selected_persona_data = personas.get(persona)
        
        # Fallback logic: if selected persona is missing or empty, try main_character
        if not selected_persona_data or not selected_persona_data.get("upright"):
            selected_persona_data = personas.get("main_character", {})

        if self.is_upright:
            return {
                "keywords": card_data.get("keywords", {}).get("upright", ""),
                "narrative": selected_persona_data.get("upright", ""),
                "traditional": card_data.get("traditional", {}).get("upright", "Traditional meaning not available.")
            }
        else:
            return {
                "keywords": card_data.get("keywords", {}).get("reversed", ""),
                "narrative": selected_persona_data.get("reversed", ""),
                "traditional": card_data.get("traditional", {}).get("reversed", "Traditional meaning not available.")
            }

    def to_dict(self, persona="main_character"):
        return {
            "name": self.name,
            "number": self.number,
            "arcana": self.arcana,
            "suit": self.suit,
            "orientation": "upright" if self.is_upright else "reversed",
            "element": self.element,
            "astrology": self.astrology,
            "kabbalah": self.kabbalah,
            "vibe_check": self.get_vibe_check(persona)
        }

    def get_element(self):
        if "Wands" in self.name:
            return "Fire"
        elif "Cups" in self.name:
            return "Water"
        elif "Swords" in self.name:
            return "Air"
        elif "Pentacles" in self.name:
            return "Earth"
        else:
            return Card.major_elements.get(self.name, "Major")

    def get_astrological_correspondence(self):
        return Card.astrological_correspondences.get(
            self.name, Card.minor_arcana_correspondences.get(self.name, "None")
        )

    def get_kabbalistic_correspondence(self):
        return Card.kabbalistic_correspondences.get(self.name, "None")

    def matches_sign(self, sign):
        if not self.astrology:
            return False
        return sign.lower() in self.astrology.lower()

    def __str__(self):
        status = " - upright" if self.is_upright else " - reversed"
        return f"    {self.name + status:<30} Arcana: {self.arcana:<10} Suit: {self.suit:<10} Number: {self.number:<5} Element: {self.element:<10} Astrology: {self.astrology:<10}"