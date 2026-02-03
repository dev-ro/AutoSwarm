import re

class IntentDetector:
    def __init__(self, personas):
        self.personas = personas

    def calculate_keyword_score(self, prompt, persona):
        prompt_lower = prompt.lower()
        keywords = persona.context_aware_triggers.get('domain_keywords', [])
        score = 0
        for kw in keywords:
            # Check for keyword or a substring if it's long enough
            kw_low = kw.lower()
            if re.search(r'\b' + re.escape(kw_low), prompt_lower):
                score += 1
        return score

    def calculate_semantic_score(self, prompt, persona):
        prompt_words = set(re.findall(r'\w+', prompt.lower()))
        if not prompt_words: return 0.0
        
        # Build a richer semantic profile for the persona
        profile_parts = [
            persona.metadata.get('role_id', ''),
            " ".join(persona.context_aware_triggers.get('domain_keywords', [])),
            " ".join(persona.voice_dna.get('preferred_descriptors', [])),
            str(persona.identity)
        ]
        profile_text = " ".join(profile_parts).lower()
        profile_words = set(re.findall(r'\w+', profile_text))
        
        intersection = prompt_words.intersection(profile_words)
        return len(intersection) / len(prompt_words)

    def detect_all_signals(self, prompt, persona):
        return {
            'S_keyword': self.calculate_keyword_score(prompt, persona),
            'S_semantic': self.calculate_semantic_score(prompt, persona)
        }