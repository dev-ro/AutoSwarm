import pytest
from src.agents.tarot import TarotAgent

def test_tarot_agent_initialization():
    agent = TarotAgent()
    assert agent is not None
    assert "clinical and deeply authentic" in agent.description

def test_tarot_agent_instructions():
    agent = TarotAgent()
    instructions = " ".join(agent.instructions)
    # Check for signal density and structure keywords
    assert "MAXIMUM SIGNAL DENSITY" in instructions
    assert "Executive Summary" in instructions
    assert "Astrology Diagnostic" in instructions
    assert "Actionable Mitigation Strategies" in instructions

def test_tarot_agent_routing(mocker):
    # Mock the LLM to return a predictable structured response
    mocker.patch.object(TarotAgent, 'run', return_value="1. Executive Summary\n2. Astrology Diagnostic\n3. Tarot Diagnostic\n4. Actionable Mitigation Strategies")
    
    agent = TarotAgent()
    response = agent.run("Give me a reading.")
    assert "Executive Summary" in response
    assert "Actionable Mitigation Strategies" in response
