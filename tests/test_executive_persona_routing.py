import os
import sys

# Ensure src module is discoverable if run from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.personality.selector import PersonalitySelector
from src.personality.schemas import NLUClassification

def test_persona_routing():
    # Construct absolute path to the persona library
    base_dir = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.join(base_dir, '..', 'src', 'personality', 'persona_library.json')
    
    # Initialize the PersonalitySelector
    selector = PersonalitySelector(persona_library_path=persona_path)
    
    # Mock NLU extraction for a "linkedin systems architect post"
    mock_nlu = NLUClassification(
        genre="linkedin systems architect post",
        target_audience="Professionals",
        emotional_tone="objective",
        detected_verbosity_requirement=2,
        detected_harshness_requirement=5
    )
    
    print(f"Mocking NLU extracted genre: '{mock_nlu.genre}'")
    
    # Select best persona based on the mocked NLU output
    best_persona = selector.select_best_persona(mock_nlu)
    
    print(f"Selector chose persona: '{best_persona.id}'")
    
    # Assert that it successfully routes to the new executive_systems_architect persona
    assert best_persona.id == "executive_systems_architect", (
        f"Routing failed! Expected 'executive_systems_architect', got '{best_persona.id}'"
    )
    
    print("\n[SUCCESS]: PersonalitySelector successfully matched and returned the 'executive_systems_architect' persona based on the genre focus.")

if __name__ == "__main__":
    test_persona_routing()
