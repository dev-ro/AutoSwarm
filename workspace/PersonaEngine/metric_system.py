import re

class MetricAwareSystem:
    def __init__(self):
        self.operators = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '==': lambda a, b: a == b,
        }

    def evaluate_triggers(self, current_metrics, personas):
        active_triggers = []
        for persona in personas:
            for trigger in persona.context_aware_triggers.get('metric_threshold_triggers', []):
                condition = trigger['condition']
                if self.eval_condition(condition, current_metrics):
                    active_triggers.append({
                        'persona': persona,
                        'condition': condition,
                        'action': trigger['action'],
                        'priority': self.determine_priority(trigger['action'])
                    })
        
        # Sort by priority
        priority_map = {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}
        active_triggers.sort(key=lambda x: priority_map.get(x['priority'], 0), reverse=True)
        return active_triggers

    def eval_condition(self, condition, metrics):
        # Syntax: <metric_key> <operator> <value>
        match = re.match(r'(\w+)\s*([><=!]+)\s*([\d\.\_]+)', condition)
        if not match:
            return False
        
        metric_key, op, value = match.groups()
        if metric_key not in metrics:
            return False
            
        metric_val = metrics[metric_key]
        # Handle underscores in numbers (e.g., 30_days)
        target_val = float(value.replace('_', ''))
        
        if op in self.operators:
            return self.operators[op](metric_val, target_val)
        return False

    def determine_priority(self, action):
        action_upper = action.upper()
        if "EMERGENCY" in action_upper or "OVERRIDE" in action_upper:
            return 'CRITICAL'
        if "DE-LEVERAGE" in action_upper or "REJECT" in action_upper:
            return 'HIGH'
        return 'MEDIUM'