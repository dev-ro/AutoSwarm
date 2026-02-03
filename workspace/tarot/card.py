from texttable import Texttable


class Card:
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

    def __init__(self, name, number, is_upright=True):
        self.name = name
        self.number = number
        self.is_upright = is_upright
        self.element = self.get_element()
        self.astrology = self.get_astrological_correspondence()
        self.kabbalah = self.get_kabbalistic_correspondence()

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
            return "Major"

    def get_astrological_correspondence(self):
        return Card.astrological_correspondences.get(
            self.name, Card.minor_arcana_correspondences.get(self.name, "None")
        )

    def get_kabbalistic_correspondence(self):
        return Card.kabbalistic_correspondences.get(self.name, "None")

    def __str__(self):
        status = " - upright" if self.is_upright else " - reversed"
        return f"    {self.name + status:<30} Number: {self.number:<5} Element: {self.element:<10} Astrology: {self.astrology:<10}"
