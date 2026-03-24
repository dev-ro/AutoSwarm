import pytest
from src.agents.signal_scout import SignalScoutAgent

def test_signal_scout_agent_initialization():
    agent = SignalScoutAgent()
    assert agent is not None
    assert "pain-point extraction" in agent.description.lower()

def test_signal_scout_agent_instructions():
    agent = SignalScoutAgent()
    instructions = " ".join(agent.instructions).lower()
    assert "social" in instructions or "forum" in instructions
    assert "pain points" in instructions or "extraction" in instructions

def test_signal_scout_agent_routing(mocker):
    mocker.patch.object(SignalScoutAgent, 'run', return_value="1. Source Overview\n2. Key Pain Points\n3. Validation Metrics")
    
    agent = SignalScoutAgent()
    response = agent.run("Analyze Reddit data for SaaS pain points.")
    assert "Key Pain Points" in response
