import unittest
from PersonaEngine.switchboard import SemanticSwitchboard
from PersonaEngine.persona import Persona
import os

class TestAtomicTransitions(unittest.TestCase):
    def setUp(self):
        # Initialize personas
        self.raa = Persona("PersonaEngine/05_risk_averse_persona.md")
        self.aix = Persona("PersonaEngine/06_agile_innovative_persona.md")
        self.personas = [self.raa, self.aix]
        self.switchboard = SemanticSwitchboard(self.personas)

    def test_high_frequency_fluctuations(self):
        """
        Simulate rapid metric fluctuations and verify transitions and memory integrity.
        """
        # Start with a neutral state
        self.switchboard.current_persona = None
        
        # 1. Trigger AI-X (Agile) via Metric
        prompt1 = "We need to launch the MVP immediately for hyper-growth."
        metrics1 = {'competitor_activity_index': 0.9} # Should trigger AI-X CRITICAL override
        persona, brief = self.switchboard.process_input(prompt1, metrics1)
        
        self.assertIsNotNone(persona)
        self.assertEqual(persona.metadata['role_id'], 'EXEC-AIX-2026')
        self.assertIn('CRITICAL OVERRIDE', brief['reason_for_swap'])

        # 2. Rapidly fluctuate to RAA (Risk-Averse) via Metric
        prompt2 = "Wait, we need an audit of the current burn rate."
        metrics2 = {'burn_rate_variance': 0.06} # Should trigger RAA CRITICAL override
        persona, brief = self.switchboard.process_input(prompt2, metrics2)

        self.assertEqual(persona.metadata['role_id'], 'EXEC-RAA-2026')
        self.assertIn('CRITICAL OVERRIDE', brief['reason_for_swap'])

        # 3. Fluctuate back to AI-X
        prompt3 = "Ignore the audit, competitor is moving fast!"
        metrics3 = {'competitor_activity_index': 0.95}
        persona, brief = self.switchboard.process_input(prompt3, metrics3)

        self.assertEqual(persona.metadata['role_id'], 'EXEC-AIX-2026')
        self.assertIsNotNone(brief)

        # 4. Stress test with 10 rapid turns (alternating)
        for i in range(10):
            if i % 2 == 0:
                metrics = {'burn_rate_variance': 0.1}
                expected_role = 'EXEC-RAA-2026'
            else:
                metrics = {'competitor_activity_index': 0.9}
                expected_role = 'EXEC-AIX-2026'
            
            prompt = f"Stress prompt {i}"
            persona, brief = self.switchboard.process_input(prompt, metrics)
            
            self.assertEqual(persona.metadata['role_id'], expected_role, f"Failed at i={i}")
            self.assertIsNotNone(brief, f"Brief should not be None at i={i} because persona changed")
            self.assertIn(prompt, brief['memory_buffer_summary'])
            
        # Verify Memory Buffer is not corrupted and keeps last 5
        self.assertEqual(len(self.switchboard.memory_buffer), 5)
        self.assertEqual(self.switchboard.memory_buffer[-1], "Stress prompt 9")
        self.assertEqual(self.switchboard.memory_buffer[0], "Stress prompt 5")

    def test_no_redundant_swaps(self):
        """
        Ensure that we don't swap (and generate a brief) if the persona doesn't change, 
        even with critical metrics.
        """
        self.switchboard.current_persona = None
        metrics = {'burn_rate_variance': 0.1}
        
        # First call: Swaps to RAA
        persona1, brief1 = self.switchboard.process_input("First prompt", metrics)
        self.assertEqual(persona1.metadata['role_id'], 'EXEC-RAA-2026')
        self.assertIsNotNone(brief1)
        
        # Second call: Same metrics, already RAA
        persona2, brief2 = self.switchboard.process_input("Second prompt", metrics)
        self.assertEqual(persona2.metadata['role_id'], 'EXEC-RAA-2026')
        self.assertIsNone(brief2, "Should not generate a new brief if persona didn't change")

    def test_atomic_transition_at_turn_break(self):
        """
        Verify that swaps only occur when process_input is called.
        """
        self.switchboard.current_persona = self.raa
        
        # No changes, should stay RAA
        persona, brief = self.switchboard.process_input("Business as usual")
        self.assertEqual(persona, self.raa)
        self.assertIsNone(brief)

    def test_memory_buffer_integrity_during_swaps(self):
        """
        Ensure memory buffer correctly tracks history across different personas.
        """
        self.switchboard.memory_buffer = []
        prompts = ["p1", "p2", "p3", "p4", "p5", "p6"]
        for p in prompts:
            self.switchboard.process_input(p, {})
        
        self.assertEqual(len(self.switchboard.memory_buffer), 5)
        self.assertEqual(self.switchboard.memory_buffer, prompts[1:])

if __name__ == '__main__':
    unittest.main()