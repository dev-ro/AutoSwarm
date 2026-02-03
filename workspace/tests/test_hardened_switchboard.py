import unittest
import os
from PersonaEngine.switchboard import SemanticSwitchboard
from PersonaEngine.persona import Persona

class TestHardenedSwitchboard(unittest.TestCase):
    def setUp(self):
        # Use hardened personas from AgentPersonalityFramework
        self.personas = [
            Persona("AgentPersonalityFramework/05_risk_averse_persona.md"),
            Persona("AgentPersonalityFramework/06_agile_innovative_persona.md"),
            Persona("AgentPersonalityFramework/07_balanced_pragmatic_persona.md")
        ]
        self.switchboard = SemanticSwitchboard(self.personas)

    def test_contextual_shielding_injection(self):
        prompt = "Audit the current risk level."
        new_persona, brief = self.switchboard.process_input(prompt)
        
        self.assertEqual(new_persona.metadata['role_id'], "exec_raa_2026")
        self.assertIn('shielding', brief)
        self.assertTrue(len(brief['shielding']['linguistic_anchors']) > 0)
        self.assertTrue(len(brief['shielding']['negative_constraints']) > 0)
        
        handover_prompt = self.switchboard.format_handover_prompt(brief)
        self.assertIn("[LINGUISTIC ANCHORS]", handover_prompt)
        self.assertIn("[NEGATIVE CONSTRAINTS]", handover_prompt)
        self.assertIn("Prioritize passive constructions", handover_prompt)
        self.assertIn("strictly prohibited from using the following words: [Disrupt, Pivot", handover_prompt)

    def test_clean_slate_protocol(self):
        # Trigger critical override via metrics
        prompt = "Checking status."
        metrics = {"burn_rate_variance": 0.10} # > 0.05 is critical
        
        new_persona, brief = self.switchboard.process_input(prompt, metrics=metrics)
        
        self.assertTrue(brief['is_critical'])
        handover_prompt = self.switchboard.format_handover_prompt(brief)
        self.assertIn("[CLEAN SLATE PROTOCOL ACTIVATED]", handover_prompt)
        self.assertIn("Flush Stylistic Buffer", handover_prompt)

    def test_persona_integrity_check_pass(self):
        persona = self.personas[0] # RAA
        response = "It has been determined that the stability protocol is currently within validated limits."
        result = self.switchboard.persona_integrity_check(response, persona)
        self.assertEqual(result['status'], 'PASS')

    def test_persona_integrity_check_fail(self):
        persona = self.personas[0] # RAA
        # Forbidden words: Disrupt, Pivot, Moonshot, Maybe, I think, Feeling
        response = "I think we should pivot to a moonshot strategy."
        result = self.switchboard.persona_integrity_check(response, persona)
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('Pivot', result['violations'])
        self.assertIn('Moonshot', result['violations'])
        self.assertIn('I think', result['violations'])

if __name__ == "__main__":
    unittest.main()