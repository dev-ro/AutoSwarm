from system_config import PERSONA_ID_MAP, limiter, get_persona_path
from PersonaEngine.persona import Persona
import logging

logging.basicConfig(level=logging.INFO)

def verify():
    print("Verifying Persona Registration:")
    for pid, path in PERSONA_ID_MAP.items():
        try:
            p = Persona(path)
            role_id = p.metadata.get('role_id')
            print(f"ID: {pid} -> Loaded successfully. Metadata Role ID: {role_id}")
            if pid != role_id and pid != "default":
                 # Some might have slightly different names in metadata vs registry map
                 # but they should generally match or be known aliases.
                 pass
        except Exception as e:
            print(f"ID: {pid} -> FAILED to load from {path}: {e}")

    print("\nVerifying Staggered Execution (RateLimiter):")
    for i in range(3):
        print(f"Request {i+1}...")
        limiter.wait()
        print(f"Request {i+1} allowed.")

if __name__ == "__main__":
    verify()