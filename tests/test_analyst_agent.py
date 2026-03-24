import pytest
from src.agents.analyst import AnalystAgent

def test_analyst_agent_initialization():
    agent = AnalystAgent()
    assert agent is not None
    assert "objective cost-benefit analysis" in agent.description

def test_analyst_agent_instructions():
    agent = AnalystAgent()
    instructions = " ".join(agent.instructions)
    assert "Final Verdict" in instructions
    assert "Objective Pros" in instructions
    assert "cost-benefit analysis" in instructions

def test_analyst_agent_routing(mocker):
    # Mock the LLM to return a predictable response
    mocker.patch.object(AnalystAgent, 'run', return_value="1. Proposal Overview\n2. Objective Pros\n3. Objective Cons\n4. ROI/Impact Projection\n5. Final Verdict: Approve")
    
    agent = AnalystAgent()
    response = agent.run("Test architecture proposal.")
    assert "Final Verdict:" in response
    assert "Objective Pros" in response
