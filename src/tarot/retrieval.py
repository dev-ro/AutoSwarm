import json
import os
from datetime import datetime

class TarotRetrieval:
    """
    Utility for querying and accessing Tarot reading records from the knowledge base.
    """
    def __init__(self, kb_path="tarot_readings.json"):
        # If we are inside the 'tarot' directory, we might need to adjust the path
        # if the KB is in the root. But let's assume it's relative to execution.
        self.kb_path = kb_path
        self.readings = []
        self.load()

    def load(self):
        """Loads readings from the JSON knowledge base file."""
        if os.path.exists(self.kb_path):
            try:
                with open(self.kb_path, 'r') as f:
                    data = json.load(f)
                    self.readings = data.get("readings", [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading knowledge base: {e}")
                self.readings = []
        else:
            self.readings = []

    def get_reading_by_id(self, reading_id):
        """Retrieve a specific reading by its ID."""
        for r in self.readings:
            if r.get("id") == reading_id:
                return r
        return None

    def get_latest_reading(self, spread=None):
        """Retrieve the most recent reading, optionally filtered by spread name."""
        filtered = self.readings
        if spread:
            filtered = [r for r in self.readings if r.get("spread") == spread]
        
        if not filtered:
            return None
            
        # Sort by timestamp descending
        return sorted(filtered, key=lambda x: x.get("timestamp", ""), reverse=True)[0]

    def get_history(self, limit=10, spread=None, persona=None):
        """Retrieve a list of recent readings with optional filters."""
        filtered = self.readings
        if spread:
            filtered = [r for r in filtered if r.get("spread") == spread]
        if persona:
            filtered = [r for r in filtered if r.get("persona") == persona]
            
        sorted_history = sorted(filtered, key=lambda x: x.get("timestamp", ""), reverse=True)
        return sorted_history[:limit]

    def search_by_card(self, card_name):
        """Search for readings that contained a specific card."""
        results = []
        for r in self.readings:
            for card in r.get("cards", []):
                if card_name.lower() in card.get("name", "").lower():
                    results.append(r)
                    break
        return results

    def get_cards_from_reading(self, reading):
        """Helper to extract card names and positions from a reading record."""
        if not reading:
            return []
        return [(c.get("position"), c.get("name"), c.get("orientation")) for c in reading.get("cards", [])]

    def get_summary_stats(self):
        """Provide basic statistics about the stored readings."""
        total = len(self.readings)
        spread_counts = {}
        for r in self.readings:
            s = r.get("spread", "unknown")
            spread_counts[s] = spread_counts.get(s, 0) + 1
            
        return {
            "total_readings": total,
            "spread_distribution": spread_counts
        }

    def format_reading_for_report(self, reading):
        """Format a reading record into a human-readable summary for a report."""
        if not reading:
            return "No reading data available."
        
        lines = []
        lines.append(f"Reading ID: {reading.get('id')}")
        lines.append(f"Date: {reading.get('timestamp')}")
        lines.append(f"Spread: {reading.get('spread')}")
        lines.append(f"Persona: {reading.get('persona')}")
        lines.append("\nCards Drawn:")
        for card in reading.get("cards", []):
            lines.append(f"- {card.get('position')}: {card.get('name')} ({card.get('orientation')})")
            vibe = card.get("vibe_check", {})
            if vibe and vibe.get("keywords"):
                lines.append(f"  Keywords: {vibe.get('keywords')}")
        
        synthesis = reading.get("synthesis", {})
        dignities = synthesis.get("elemental_dignities", {})
        lines.append(f"\nElemental Dignities: {dignities}")
        
        cusp = synthesis.get("cusp_analysis")
        if cusp:
            lines.append(f"Cusp Analysis: {cusp.get('summary')}")
            
        return "\n".join(lines)

    def save_reading(self, reading_record):
        """
        Append a new reading record to the knowledge base.
        Validates the record against the basic required structure.
        """
        required_keys = ["id", "timestamp", "spread", "persona", "cards", "synthesis"]
        for key in required_keys:
            if key not in reading_record:
                raise ValueError(f"Missing required field: {key}")

        # Check for duplicates
        if any(r.get("id") == reading_record["id"] for r in self.readings):
            print(f"Reading with ID {reading_record['id']} already exists. Skipping save.")
            return False

        self.readings.append(reading_record)
        
        try:
            with open(self.kb_path, 'w') as f:
                json.dump({"readings": self.readings}, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving knowledge base: {e}")
            return False