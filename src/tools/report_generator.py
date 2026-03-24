import json
import os
import argparse
from jinja2 import Environment, FileSystemLoader

# Robust import strategy for the tarot package
try:
    from tarot.retrieval import TarotRetrieval
except (ImportError, ModuleNotFoundError):
    try:
        # Fallback for when running from within the tarot directory
        from retrieval import TarotRetrieval
    except (ImportError, ModuleNotFoundError):
        # Final fallback for unusual execution environments
        TarotRetrieval = None

class ReportGenerator:
    """
    Automates the population of the Spiritual Guidance Report Template 
    using structured JSON data from the tarot knowledge base.
    """
    def __init__(self, template_path, kb_path):
        if TarotRetrieval is None:
            raise ImportError("Could not import TarotRetrieval. Ensure the 'tarot' package is in your PYTHONPATH.")

        # Ensure paths are absolute
        self.template_path = os.path.abspath(template_path)
        self.kb_path = os.path.abspath(kb_path)
        
        template_dir = os.path.dirname(self.template_path)
        template_file = os.path.basename(self.template_path)
        
        self.retriever = TarotRetrieval(self.kb_path)
        
        # Configure Jinja2 environment with FileSystemLoader for robust template resolution
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True, 
            lstrip_blocks=True
        )
        self.template_name = template_file
        
    def generate_report(self, reading_id=None, output_path=None):
        """
        Fetches a reading and populates the template.
        """
        # Reload to get the latest data
        self.retriever.load()
        
        if reading_id:
            reading = self.retriever.get_reading_by_id(reading_id)
        else:
            reading = self.retriever.get_latest_reading()
            
        if not reading:
            print(f"Error: No reading found.")
            return None
            
        # Prepare data for template
        template_data = self._prepare_data(reading)
        
        # Load and render template
        try:
            template = self.env.get_template(self.template_name)
            rendered_report = template.render(**template_data)
        except Exception as e:
            print(f"Error rendering template: {e}")
            return None
        
        # Determine output path relative to the root of the project
        if not output_path:
            # Get the project root (assuming report_generator.py is at the root)
            root_dir = os.path.dirname(os.path.abspath(__file__))
            reports_dir = os.path.join(root_dir, "reports")
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            output_path = os.path.join(reports_dir, f"Spiritual_Guidance_Report_{reading['id']}.md")
        else:
            output_path = os.path.abspath(output_path)
            
        # Save report
        try:
            with open(output_path, 'w') as f:
                f.write(rendered_report)
            print(f"Success: Report generated at {output_path}")
            return output_path
        except IOError as e:
            print(f"Error saving report: {e}")
            return None

    def _prepare_data(self, reading):
        """
        Maps raw reading data to template placeholders.
        """
        synthesis = reading.get("synthesis", {})
        dignities = synthesis.get("elemental_dignities", {})
        persona = reading.get("persona", "Seeker")
        
        # Generate elemental summary based on dignities
        strengthen = dignities.get("strengthen", 0)
        weaken = dignities.get("weaken", 0)
        neutral = dignities.get("neutral", 0)
        
        if strengthen > (weaken + neutral):
            elemental_summary = f"The reading shows an overwhelming degree of elemental synergy ({strengthen} strengthening combinations). The universe is providing massive tailwinds for your current trajectory."
            if persona == "main_character":
                elemental_summary += " The algorithm is finally in your favor; your digital aura is high-signal."
        elif strengthen > weaken:
            elemental_summary = f"The reading shows a high degree of elemental synergy ({strengthen} strengthening). This suggests that your current environment is providing the necessary support to catalyze your growth."
            if persona == "main_character":
                elemental_summary += " Your frequency is aligned with the prevailing network trends."
        elif weaken > strengthen:
            elemental_summary = f"Elemental friction is high ({weaken} weakening combinations). You may feel like you are navigating against the current. This friction is a call for refinement and resilience."
            if persona == "main_character":
                elemental_summary += " You're hitting a firewall; it's time to debug your intentions."
        else:
            elemental_summary = f"Elemental energies are balanced ({neutral} neutral). This is a period of stabilization, allowing you to integrate recent changes without external pressure."
            if persona == "main_character":
                elemental_summary += " You're in a low-latency state, perfect for background processing."
            
        cusp = synthesis.get("cusp_analysis", {})
        cusp_summary = cusp.get("summary", "No cusp-relevant cards found.")
        
        cards = reading.get("cards", [])
        
        # Check if any card is cusp-relevant
        has_cusp_data = any(c.get("cusp_relevant", False) for c in cards)
        
        # Enhanced Integration Advice Logic
        integration_advice = "Stay grounded in your vision. The current alignment suggests that slow, intentional progress is favored over impulsive changes."
        
        # Try to find Advice and Challenge specifically
        advice_card = next((c for c in cards if c['position'].lower() == 'advice'), None)
        challenge_card = next((c for c in cards if c['position'].lower() == 'challenge'), None)
        
        if advice_card and challenge_card:
            adv_name = advice_card['name']
            adv_narrative = advice_card.get('vibe_check', {}).get('narrative', '')
            cha_vibe = challenge_card.get('vibe_check', {}).get('keywords', '')
            
            # Synthesize a 2-3 sentence Action Plan
            # Remove any trailing "---" or excessive whitespace from narratives
            adv_narrative = adv_narrative.split("---")[0].strip()
            
            integration_advice = (
                f"To navigate the current {challenge_card['name']} hurdle ({cha_vibe.lower()}), "
                f"you must lean into the strategy of {adv_name}. {adv_narrative} "
                "By integrating this perspective, you transform the challenge into a catalyst for your next level."
            )

        return {
            "spread_name": reading.get("spread", "Tarot").replace("_", " ").title(),
            "timestamp": reading.get("timestamp", "").replace("T", " ")[:19],
            "persona": persona,
            "reading_id": reading.get("id", ""),
            "strengthen_count": strengthen,
            "weaken_count": weaken,
            "neutral_count": neutral,
            "elemental_summary": elemental_summary,
            "cusp_summary": cusp_summary,
            "has_cusp_data": has_cusp_data,
            "cards": cards,
            "integration_advice": integration_advice
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Spiritual Guidance Report.")
    parser.add_argument("--id", help="The ID of the reading to generate a report for.")
    parser.add_argument("--template", default="spiritual_guidance_template.md", help="Path to the Markdown template.")
    parser.add_argument("--kb", default="tarot/tarot_readings.json", help="Path to the tarot readings knowledge base.")
    parser.add_argument("--output", help="Path to save the generated report.")
    
    args = parser.parse_args()
    
    try:
        generator = ReportGenerator(args.template, args.kb)
        generator.generate_report(reading_id=args.id, output_path=args.output)
    except Exception as e:
        print(f"Error: {e}")