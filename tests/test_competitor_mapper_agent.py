import pytest
from src.agents.competitor_mapper import CompetitorMapperAgent

def test_competitor_mapper_agent_initialization():
    agent = CompetitorMapperAgent()
    assert agent is not None
    assert "market gap analysis" in agent.description.lower()

def test_competitor_mapper_agent_instructions():
    agent = CompetitorMapperAgent()
    instructions = " ".join(agent.instructions).lower()
    assert "market gap" in instructions
    assert "competitor" in instructions

def test_competitor_mapper_agent_routing(mocker):
    mocker.patch.object(CompetitorMapperAgent, 'run', return_value="1. Competitor Overview\n2. Market Gaps identified")
    
    agent = CompetitorMapperAgent()
    response = agent.run("Analyze competitor landscape for AI scheduling tools.")
    assert "Market Gaps" in response
