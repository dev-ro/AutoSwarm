import re
import yaml

class Persona:
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = {}
        self.identity = {}
        self.voice_dna = {}
        self.metric_awareness = {}
        self.architect_parameters = {}
        self.constraints = []
        self.context_aware_triggers = {
            'domain_keywords': [],
            'metric_threshold_triggers': [],
            'scenario_triggers': {}
        }
        self.load_from_markdown(file_path)

    def load_from_markdown(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read().replace('\r', '')

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
        
        for block in yaml_blocks:
            try:
                data = yaml.safe_load(block)
                if not data: continue
                
                # Support new flat structure or nested structure
                if 'identity_layer' in data:
                    self.identity = data['identity_layer']
                elif 'identity' in data:
                    self.identity = data['identity']
                
                if 'voice_dna' in data:
                    self.voice_dna = data['voice_dna']
                elif self.identity and 'voice_dna' in self.identity:
                    self.voice_dna = self.identity['voice_dna']
                
                if 'metric_awareness' in data:
                    self.metric_awareness = data['metric_awareness']
                
                if 'architect_parameters' in data:
                    self.architect_parameters = data['architect_parameters']
                
                if 'constraint_layer' in data:
                    self.constraints = data['constraint_layer']
                
                if 'context_aware_triggers' in data:
                    triggers = data['context_aware_triggers']
                    # Normalize metric triggers
                    if 'metric_threshold_triggers' in triggers:
                        normalized_metrics = []
                        for mt in triggers['metric_threshold_triggers']:
                            if isinstance(mt, dict):
                                condition = mt.get('if') or mt.get('condition')
                                action = mt.get('action')
                                if condition and action:
                                    normalized_metrics.append({'condition': condition, 'action': action})
                        triggers['metric_threshold_triggers'] = normalized_metrics
                    
                    self.context_aware_triggers.update(triggers)

                if 'profile_id' in data:
                    self.metadata['role_id'] = data['profile_id']
                elif 'role_id' in data:
                    self.metadata['role_id'] = data['role_id']

            except yaml.YAMLError:
                continue

        # Legacy Extraction for Markdown sections
        if 'role_id' not in self.metadata:
            role_id_match = re.search(r'\*\*Role ID:\*\* (.*)', content)
            if role_id_match:
                self.metadata['role_id'] = role_id_match.group(1).strip()

        if 'role_id' in self.metadata and 'role_id' not in self.identity:
            self.identity['role_id'] = self.metadata['role_id']

        # Extract Constraints if not already loaded from YAML
        if not self.constraints:
            constraints_match = re.search(r'## 5. Constraint Layer \(Rules\)\n(.*?)(?=\n##|$)', content, re.DOTALL)
            if constraints_match:
                self.constraints = [l.strip('* ').strip() for l in constraints_match.group(1).split('\n') if l.strip()]

        # Legacy Context-Aware Triggers (if not loaded from YAML)
        if not self.context_aware_triggers['domain_keywords']:
            triggers_section = re.search(r'## 6. Context-Aware Triggers \(Semantic Switchboard\)\n(.*?)(?=\n---|$)', content, re.DOTALL)
            if triggers_section:
                triggers_text = triggers_section.group(1)
                # Keywords
                kw_match = re.search(r'Keyword Triggers.*\[(.*?)\]', triggers_text)
                if kw_match:
                    self.context_aware_triggers['domain_keywords'] = [k.strip().strip('"').strip("'") for k in kw_match.group(1).split(',')]
                # Metric Triggers
                mt_matches = re.findall(r'`if (.*?)`: (.*)', triggers_text)
                for cond, action in mt_matches:
                    self.context_aware_triggers['metric_threshold_triggers'].append({
                        'condition': cond.strip(),
                        'action': action.strip()
                    })
                # Scenario Triggers
                st_matches = re.findall(r'User mentions "(.*?)" -> Execute `(.*?)`', triggers_text)
                for scenario, execution in st_matches:
                    self.context_aware_triggers['scenario_triggers'][scenario] = execution

    def __repr__(self):
        return f"<Persona {self.metadata.get('role_id', 'Unknown')}>"