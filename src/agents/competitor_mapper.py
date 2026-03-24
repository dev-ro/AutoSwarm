from agno.agent import Agent
from src.core.models import get_executive_model # Type: ignore

class CompetitorMapperAgent(Agent):
    def __init__(self, name: str = "Competitor Mapper"):
        super().__init__(
            model=get_executive_model(),
            description="Agent for market gap analysis and competitor landscape mapping.",
            instructions=[
                "You are an expert at competitor research and market gap analysis.",
                "Your objective is to identify weaknesses, missing features, and structural flaws in competitor products.",
                "Output structured analysis highlighting actionable market gaps we can exploit."
            ],
            tools=[]
        )
