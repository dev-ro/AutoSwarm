import sys
import os
import json
from datetime import datetime

# Robust import strategy for internal modules
# We try absolute imports first (standard for packages), then fallback to local imports.
try:
    from tarot.deck import Deck
    from tarot.reading import Reading
    from tarot.retrieval import TarotRetrieval
except (ImportError, ModuleNotFoundError):
    # Fallback for when the package is not installed or root is not in path
    try:
        from deck import Deck
        from reading import Reading
        from retrieval import TarotRetrieval
    except ImportError:
        # If we are really lost, try to find the directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        from deck import Deck
        from reading import Reading
        from retrieval import TarotRetrieval

def main():
    deck = Deck()
    reading = Reading(deck)

    # Use celtic_cross as the default spread
    spread_name = "celtic_cross"
    persona = "main_character"
    target_signs = None
    
    # Simple CLI argument handling
    if len(sys.argv) > 1:
        spread_name = sys.argv[1]
    
    if len(sys.argv) > 2:
        persona = sys.argv[2]

    if spread_name not in reading.spreads:
        print(f"Spread '{spread_name}' not found. Defaulting to 'celtic_cross'.")
        spread_name = "celtic_cross"

    print(f"Executing reading: {spread_name} for persona: {persona}")
    print(deck.print_deck_description())
    print("="*100)
    
    # Perform the reading
    spread = reading.spreads[spread_name]
    deck.shuffle_deck()
    spread.draw_cards(deck)
    spread.display(target_signs=target_signs)
    
    # Capture analysis data
    analysis_data = spread.get_analysis_data(target_signs=target_signs, persona=persona)
    
    # Persist to knowledge base
    now = datetime.now()
    reading_record = {
        "id": now.strftime("%Y%m%d%H%M%S%f"),
        "timestamp": now.isoformat(),
        "spread": spread_name,
        "persona": persona,
        "cards": analysis_data["cards"],
        "synthesis": analysis_data["synthesis"]
    }
    
    # Use absolute path relative to this script's location for the KB
    current_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(current_dir, "tarot_readings.json")
    retrieval = TarotRetrieval(kb_path)
    
    if retrieval.save_reading(reading_record):
        print(f"Reading successfully persisted to knowledge base (ID: {reading_record['id']})")
        
        # Automate Markdown report generation
        print("Generating Markdown report...")
        
        # Enhanced Error Resilience
        try:
            # Robust Import Strategy for ReportGenerator
            ReportGenerator = None
            try:
                from report_generator import ReportGenerator
            except ImportError:
                # Fallback: manually import by path if needed, but avoid sys.path manipulation if possible
                root_dir = os.path.abspath(os.path.join(current_dir, ".."))
                report_gen_path = os.path.join(root_dir, "report_generator.py")
                
                if os.path.exists(report_gen_path):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("report_generator", report_gen_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    ReportGenerator = module.ReportGenerator
            
            if ReportGenerator:
                root_dir = os.path.abspath(os.path.join(current_dir, ".."))
                template_path = os.path.join(root_dir, "spiritual_guidance_template.md")
                
                if not os.path.exists(template_path):
                    print(f"Warning: Template not found at {template_path}. Skipping report generation.")
                else:
                    generator = ReportGenerator(template_path, kb_path)
                    generator.generate_report(reading_id=reading_record['id'])
            else:
                print("Warning: could not load ReportGenerator. Skipping report generation.")
                
        except Exception as e:
            print(f"Failed to generate report: {e}")
    else:
        print("Failed to persist reading.")

    print("="*100)
    print()

if __name__ == "__main__":
    main()