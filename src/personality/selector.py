import json
from typing import List, Optional
from .schemas import Persona, NLUClassification

class PersonalitySelector:
    def __init__(self, persona_library_path: str):
        self.persona_library_path = persona_library_path
        self.personas = self._load_personas()

    def _load_personas(self) -> List[Persona]:
        with open(self.persona_library_path, 'r') as f:
            data = json.load(f)
            return [Persona(**p) for p in data]

    def sample_text(self, text: str, max_tokens: int = 1000) -> str:
        """
        Samples the first N tokens of the text for NLU analysis.
        Uses a simple character-based approximation (1 token ~= 4 characters).
        """
        char_limit = max_tokens * 4
        return text[:char_limit]

    def get_nlu_prompt(self, user_input: str) -> str:
        sampled_input = self.sample_text(user_input)
        return f"""Analyze the following sample of user input to determine the most appropriate editing persona.
Extract the genre, target audience, and emotional tone. 
Also suggest a verbosity level (1-5, where 1 is extremely concise and 5 is very detailed) 
and a critique harshness level (1-5, where 1 is very gentle and 5 is brutally honest).

Sample Input: "{sampled_input}"

Your output must be a valid JSON object with the following keys:
- genre
- target_audience
- emotional_tone
- detected_verbosity_requirement (1-5)
- detected_harshness_requirement (1-5)
"""

    def select_best_persona(self, nlu_result: NLUClassification) -> Persona:
        """
        Logic to match NLU results to the best available persona in the library.
        Currently uses a simple genre matching and then finds the closest verbosity/harshness match.
        """
        # 1. Filter by genre (case-insensitive)
        matching_personas = [
            p for p in self.personas 
            if any(nlu_result.genre.lower() in g.lower() or g.lower() in nlu_result.genre.lower() for g in p.genre_focus)
        ]

        if not matching_personas:
            # Fallback to all if no genre match
            matching_personas = self.personas

        # 2. Score based on verbosity and harshness distance
        def score(persona: Persona):
            v_diff = abs(persona.verbosity - (nlu_result.detected_verbosity_requirement or 3))
            h_diff = abs(persona.critique_harshness - (nlu_result.detected_harshness_requirement or 3))
            return v_diff + h_diff

        best_persona = min(matching_personas, key=score)
        return best_persona

    def generate_system_prompt(self, persona: Persona, nlu_result: NLUClassification) -> str:
        """
        Combines the persona's template with specific NLU findings to create a tailored system prompt.
        """
        prompt = persona.system_prompt_template
        prompt += f"\n\nTargeting Audience: {nlu_result.target_audience}"
        prompt += f"\nDetected Tone: {nlu_result.emotional_tone}"
        prompt += f"\nDesired Verbosity: {persona.verbosity}/5"
        prompt += f"\nDesired Harshness: {persona.critique_harshness}/5"
        
        return prompt
