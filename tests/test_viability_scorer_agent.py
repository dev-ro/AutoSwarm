import pytest
from src.agents.viability_scorer import ViabilityScorerAgent

def test_viability_scorer_agent_initialization():
    agent = ViabilityScorerAgent()
    assert agent is not None
    assert "icp generation" in agent.description.lower()

def test_viability_scorer_agent_instructions():
    agent = ViabilityScorerAgent()
    instructions = " ".join(agent.instructions).lower()
    assert "icp" in instructions or "ideal customer profile" in instructions
    assert "validation test" in instructions

def test_viability_scorer_agent_routing(mocker):
    mocker.patch.object(ViabilityScorerAgent, 'run', return_value="1. ICP Profile\n2. Validation Test Plan\n3. Viability Score: 85/100")
    
    agent = ViabilityScorerAgent()
    response = agent.run("Generate ICP and validation tests for AI scheduling tool.")
    assert "Validation Test Plan" in response
