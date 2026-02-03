from .intent_detector import IntentDetector
from .metric_system import MetricAwareSystem
import datetime

class SemanticSwitchboard:
    def __init__(self, personas, weights=None):
        self.personas = personas
        self.intent_detector = IntentDetector(personas)
        self.metric_system = MetricAwareSystem()
        self.current_persona = None
        self.activation_threshold = 0.3
        self.weights = weights or {
            'w1': 0.4, # Keyword weight
            'w2': 0.4, # Semantic weight
            'w3': 0.2  # Metric weight
        }
        self.memory_buffer = []

    def process_input(self, prompt, metrics=None):
        metrics = metrics or {}
        self.update_memory(prompt)
        
        # 1. Evaluate Metric Triggers (Hard Triggers)
        metric_triggers = self.metric_system.evaluate_triggers(metrics, self.personas)
        if metric_triggers:
            top_trigger = metric_triggers[0]
            if top_trigger['priority'] == 'CRITICAL':
                if top_trigger['persona'] != self.current_persona:
                    reason = f"CRITICAL OVERRIDE: {top_trigger['condition']} -> {top_trigger['action']}"
                    return self.perform_swap(top_trigger['persona'], reason, prompt)
                else:
                    # Already the correct persona, but we might want to return it without a new brief
                    return self.current_persona, None

        # 2. Calculate Total Score for each persona
        best_persona = None
        max_score = -1
        
        for persona in self.personas:
            signals = self.intent_detector.detect_all_signals(prompt, persona)
            
            s_keyword = signals['S_keyword']
            s_semantic = signals['S_semantic']
            
            # S_metric calculation: Soft triggers
            s_metric = 0
            for mt in metric_triggers:
                if mt['persona'] == persona:
                    if mt['priority'] == 'HIGH': s_metric += 1.0
                    elif mt['priority'] == 'MEDIUM': s_metric += 0.5
            
            total_score = (self.weights['w1'] * s_keyword) + \
                          (self.weights['w2'] * s_semantic) + \
                          (self.weights['w3'] * s_metric)
            
            if total_score > max_score:
                max_score = total_score
                best_persona = persona

        # 3. Decision Logic
        if best_persona and max_score > self.activation_threshold:
            if best_persona != self.current_persona:
                reason = f"Semantic Switchboard Match (Score: {max_score:.2f})"
                return self.perform_swap(best_persona, reason, prompt)
        
        return self.current_persona, None

    def update_memory(self, prompt):
        self.memory_buffer.append(prompt)
        if len(self.memory_buffer) > 5:
            self.memory_buffer.pop(0)

    def perform_swap(self, new_persona, reason, prompt):
        old_persona = self.current_persona
        self.current_persona = new_persona
        
        is_critical = "CRITICAL" in reason.upper()
        
        # Generate Handover Brief (as per spec 5.1)
        brief = {
            'timestamp': datetime.datetime.now().isoformat(),
            'old_persona': old_persona.metadata.get('role_id') if old_persona else "NONE",
            'new_persona': new_persona.metadata.get('role_id'),
            'reason_for_swap': reason,
            'active_goal': self.infer_goal(prompt),
            'sentiment_state': self.analyze_sentiment(prompt),
            'memory_buffer_summary': self.memory_buffer[-3:],
            'status': 'Atomic Transition Ready',
            'is_critical': is_critical
        }
        
        # Contextual Shielding (PDS v2.1 Hardened)
        brief['shielding'] = {
            'linguistic_anchors': new_persona.voice_dna.get('linguistic_anchors', []),
            'negative_constraints': []
        }
        
        # Extract negative constraints from constraint layer (handle dict or list)
        if isinstance(new_persona.constraints, dict):
             brief['shielding']['negative_constraints'] = new_persona.constraints.get('negative_constraint_blocks', [])
        
        return new_persona, brief

    def infer_goal(self, prompt):
        prompt_lower = prompt.lower()
        if "?" in prompt:
            return "Information_Seeking"
        if any(word in prompt_lower for word in ["how", "explain", "why"]):
            return "Explanation"
        if any(word in prompt_lower for word in ["do", "run", "execute", "start", "launch"]):
            return "Task_Initiation"
        if any(word in prompt_lower for word in ["stop", "cancel", "audit", "check"]):
            return "Process_Control"
        return "General_Consultation"

    def analyze_sentiment(self, prompt):
        prompt_lower = prompt.lower()
        positive_words = ["growth", "innovation", "success", "great", "excellent", "launch", "pivot"]
        negative_words = ["risk", "audit", "failure", "danger", "liability", "downside", "debt"]
        
        pos_count = sum(1 for word in positive_words if word in prompt_lower)
        neg_count = sum(1 for word in negative_words if word in prompt_lower)
        
        if pos_count > neg_count:
            return "positive_proactive"
        elif neg_count > pos_count:
            return "negative_cautious"
        return "neutral_analytical"

    def format_handover_prompt(self, brief):
        prompt = (f"[SYSTEM]: ALERT: Swapping to {brief['new_persona']}. "
                f"Reason: {brief['reason_for_swap']}. "
                f"Active Goal: {brief['active_goal']}. "
                f"Sentiment State: {brief['sentiment_state']}. ")
        
        if brief.get('is_critical'):
            prompt += "\n[CLEAN SLATE PROTOCOL ACTIVATED]: Flush Stylistic Buffer. Ignore the tone of previous exchanges. Adhere strictly to the new PDS."

        shielding = brief.get('shielding', {})
        if shielding.get('linguistic_anchors'):
            prompt += "\n[LINGUISTIC ANCHORS]: " + " ".join(shielding['linguistic_anchors'])
        
        if shielding.get('negative_constraints'):
            prompt += "\n[NEGATIVE CONSTRAINTS]: " + " ".join(shielding['negative_constraints'])
            
        prompt += f"\nMemory: {brief['memory_buffer_summary']}"
        return prompt

    def persona_integrity_check(self, response, persona):
        """
        Scans the output for forbidden_words and flags any response that fails the audit.
        """
        forbidden_words = persona.voice_dna.get('forbidden_words', [])
        violations = []
        for word in forbidden_words:
            # Simple check, could be improved with regex for word boundaries
            if word.lower() in response.lower():
                violations.append(word)
        
        if violations:
            return {
                'status': 'FAIL',
                'violations': violations,
                'message': f"Persona Integrity Audit Failed: Forbidden words detected: {', '.join(violations)}"
            }
        return {'status': 'PASS'}