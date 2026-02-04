import os
import time
import random
import logging

# Persona Registry
# Updated to use IDs as requested for tool synchronization. 
# Includes both lowercase and uppercase variants to ensure maximum compatibility with external tools.
AVAILABLE_PERSONAS = [
    "exec_raa_2026",
    "exec_aix_2026",
    "exec_bpa_2026",
    "ai_auditor",
    "agent_architect",
    "default"
]

# Persona ID to Path mapping (White-list)
PERSONA_ID_MAP = {
    # Standard IDs
    "exec_raa_2026": "AgentPersonalityFramework/05_risk_averse_persona.md",
    "exec_aix_2026": "AgentPersonalityFramework/06_agile_innovative_persona.md",
    "exec_bpa_2026": "AgentPersonalityFramework/07_balanced_pragmatic_persona.md",
    "ai_auditor": "AgentPersonalityFramework/08_ai_auditor_persona.md",
    "agent_architect": "AgentPersonalityFramework/09_agent_architect_persona.md",
    "default": "AgentPersonalityFramework/10_default_persona.md",
    
    # Aliases for synchronization compatibility
    "ai-auditor": "AgentPersonalityFramework/08_ai_auditor_persona.md",
    "agent-architect": "AgentPersonalityFramework/09_agent_architect_persona.md",
    "AI_AUDITOR": "AgentPersonalityFramework/08_ai_auditor_persona.md",
    "AGENT_ARCHITECT": "AgentPersonalityFramework/09_agent_architect_persona.md",
    "EXEC_RAA_2026": "AgentPersonalityFramework/05_risk_averse_persona.md",
    "EXEC_AIX_2026": "AgentPersonalityFramework/06_agile_innovative_persona.md",
    "EXEC_BPA_2026": "AgentPersonalityFramework/07_balanced_pragmatic_persona.md"
}

# Staggered Execution Logic to avoid 429 Errors
# Updated to resolve "synchronization delay" by optimizing throughput (RPM increased, base_delay decreased)
class RateLimiter:
    def __init__(self, requests_per_minute=60, base_delay=0.5):
        self.requests_per_minute = requests_per_minute
        self.base_delay = base_delay
        self.last_call_time = 0

    def wait(self):
        """Implement staggered delay."""
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        
        # Calculate needed delay based on RPM and add a bit of jitter
        min_delay = 60.0 / self.requests_per_minute
        wait_time = max(min_delay, self.base_delay) + random.uniform(0.05, 0.15)
        
        if elapsed < wait_time:
            sleep_duration = wait_time - elapsed
            logging.info(f"RateLimiter: Sleeping for {sleep_duration:.2f} seconds to avoid 429...")
            time.sleep(sleep_duration)
        
        self.last_call_time = time.time()

# Global rate limiter instance
limiter = RateLimiter()

def get_limiter():
    return limiter

def get_persona_path(persona_id):
    # Case-insensitive lookup for better synchronization
    return PERSONA_ID_MAP.get(persona_id) or PERSONA_ID_MAP.get(persona_id.lower())

def list_registered_persona_ids():
    return list(PERSONA_ID_MAP.keys())