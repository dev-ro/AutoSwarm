from typing import Dict, Type
from .state import AgentState
from src.personality.selector import PersonalitySelector
from src.personality.schemas import NLUClassification
from .constitution_loader import ConstitutionLoader
from .editors import BaseEditor, SciFiEditor, NoirEditor, FantasyEditor, AcademicEditor, GenericEditor

class WorkflowSupervisor:
    def __init__(self, persona_library_path: str):
        self.selector = PersonalitySelector(persona_library_path)
        self.loader = ConstitutionLoader()
        self.editors: Dict[str, BaseEditor] = {
            "sci-fi": SciFiEditor(),
            "noir": NoirEditor(),
            "fantasy": FantasyEditor(),
            "academic": AcademicEditor(),
            "generic": GenericEditor()
        }

    def selector_node(self, state: AgentState) -> AgentState:
        print("--- Supervisor: Analyzing Input (NLU Sampling) ---")
        
        # Sampling the first 1000 tokens (approx 4000 characters)
        sampled_text = self.selector.sample_text(state['input_text'], max_tokens=1000)
        
        text_lower = sampled_text.lower()
        if any(w in text_lower for w in ["starship", "alien", "robot", "quantum", "galaxy", "space", "future"]):
            genre = "Sci-Fi"
            v, h = 4, 4
        elif any(w in text_lower for w in ["rain", "whiskey", "gun", "shadow", "dame", "case", "detective", "alley"]):
            genre = "Noir"
            v, h = 2, 5
        elif any(w in text_lower for w in ["dragon", "magic", "sword", "kingdom", "spell", "ancient", "king"]):
            genre = "Fantasy"
            v, h = 5, 2
        elif any(w in text_lower for w in ["research", "evidence", "data", "analysis", "conclusion", "study", "academic"]):
            genre = "Academic"
            v, h = 4, 3
        else:
            genre = "General"
            v, h = 2, 3

        nlu_result = NLUClassification(
            genre=genre,
            target_audience="General Readers",
            emotional_tone="Neutral" if genre == "General" else "Genre-Specific",
            detected_verbosity_requirement=v,
            detected_harshness_requirement=h
        )
        
        state['classification'] = nlu_result
        
        # Select persona
        best_persona = self.selector.select_best_persona(nlu_result)
        state['selected_persona'] = best_persona
        
        # Load constitution
        state['genre_constitution'] = self.loader.get_constitution(nlu_result.genre)
        
        # Tiered Routing Logic
        genre_key = nlu_result.genre.lower()
        if "sci-fi" in genre_key:
            state['next_node'] = "sci-fi"
        elif "noir" in genre_key:
            state['next_node'] = "noir"
        elif "fantasy" in genre_key:
            state['next_node'] = "fantasy"
        elif "academic" in genre_key:
            state['next_node'] = "academic"
        else:
            state['next_node'] = "generic"
            
        print(f"Supervisor decided: Route to {state['next_node']} using persona {best_persona.name}")
        return state

    def run(self, input_text: str) -> AgentState:
        state: AgentState = {
            "input_text": input_text,
            "classification": None,
            "selected_persona": None,
            "genre_constitution": None,
            "editor_output": None,
            "critique_points": [],
            "next_node": "selector",
            "history": []
        }
        
        current_node = "selector"
        while current_node != "END":
            state['history'].append({"node": current_node})
            if current_node == "selector":
                state = self.selector_node(state)
            elif current_node in self.editors:
                state = self.editors[current_node].process(state)
            else:
                break
            current_node = state['next_node']
        return state
