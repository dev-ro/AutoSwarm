
import os
from dotenv import load_dotenv
load_dotenv()

from src.agents.executive import get_executive_agent
from src.agents.researcher import get_research_agent
from src.agents.coder import get_coder_agent
from src.core.config import MODEL

def test_model_parity():
    print(f"Expected Model from Config: {MODEL}")
    
    executive = get_executive_agent()
    researcher = get_research_agent()
    coder = get_coder_agent()
    
    agents = [
        ("Executive", executive),
        ("Researcher", researcher),
        ("Coder", coder)
    ]
    
    success = True
    for name, agent in agents:
        actual_model = agent.model.id
        print(f"Agent {name} is using model: {actual_model}")
        if actual_model != MODEL:
            print(f"[FAIL]: {name} model mismatch!")
            success = False
        else:
            print(f"[PASS]: {name} model matches.")
            
    if success:
        print("\nAll agents are synchronized with the global model configuration.")
    else:
        exit(1)

if __name__ == "__main__":
    test_model_parity()
