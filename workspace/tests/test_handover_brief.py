import sys
import os
import time
import unittest
from PersonaEngine.switchboard import SemanticSwitchboard
from PersonaEngine.persona import Persona

class TestHandoverBrief(unittest.TestCase):
    def setUp(self):
        # Load personas
        self.personas = [
            Persona("PersonaEngine/05_risk_averse_persona.md"),
            Persona("PersonaEngine/06_agile_innovative_persona.md"),
            Persona("PersonaEngine/07_balanced_pragmatic_persona.md")
        ]
        self.switchboard = SemanticSwitchboard(self.personas)

    def test_handover_latency(self):
        # Target a swap by using keywords for Agile persona
        prompt = "We need to focus on Growth and Velocity! Launch the MVP now to achieve Hyper-growth."
        
        start_time = time.time()
        new_persona, brief = self.switchboard.process_input(prompt)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        print(f"Swap Latency: {latency_ms:.2f}ms")
        
        self.assertIsNotNone(new_persona, "Persona swap should have occurred")
        self.assertEqual(new_persona.metadata['role_id'], "EXEC-AIX-2026")
        self.assertLess(latency_ms, 50, f"Handover took longer than 50ms: {latency_ms:.2f}ms")

    def test_brief_content(self):
        # Trigger swap to Risk-Averse
        prompt = "We must conduct an Audit to mitigate Risk and ensure Compliance."
        metrics = {"burn_rate_variance": 0.06} # This should trigger critical override
        
        new_persona, brief = self.switchboard.process_input(prompt, metrics=metrics)
        
        self.assertIsNotNone(brief)
        self.assertEqual(brief['new_persona'], "EXEC-RAA-2026")
        self.assertIn("CRITICAL OVERRIDE", brief['reason_for_swap'])
        
        # Verify Goal Inference (Audit/Check triggers Process_Control)
        self.assertEqual(brief['active_goal'], "Process_Control")
        
        # Verify Sentiment (Audit/Risk trigger negative_cautious)
        self.assertEqual(brief['sentiment_state'], "negative_cautious")

    def test_goal_inference_inquiry(self):
        prompt = "What are the risks of this project?"
        goal = self.switchboard.infer_goal(prompt)
        self.assertEqual(goal, "Information_Seeking")

    def test_sentiment_positive(self):
        prompt = "This innovation is a great success and we are ready to launch!"
        sentiment = self.switchboard.analyze_sentiment(prompt)
        self.assertEqual(sentiment, "positive_proactive")

    def test_adoption_prompt(self):
        prompt = "Audit the current risk level."
        new_persona, brief = self.switchboard.process_input(prompt)
        if not brief:
             new_persona, brief = self.switchboard.perform_swap(self.personas[0], "Manual Trigger", prompt)
             
        system_prompt = self.switchboard.format_handover_prompt(brief)
        self.assertIn("ALERT: Swapping to", system_prompt)
        self.assertIn("Active Goal: Process_Control", system_prompt)
        self.assertIn("Sentiment State: negative_cautious", system_prompt)

if __name__ == "__main__":
    unittest.main()