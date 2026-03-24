from agno.agent import Agent
from src.core.models import get_executive_model # Type: ignore

class ViabilityScorerAgent(Agent):
    def __init__(self, name: str = "Viability Scorer"):
        super().__init__(
            model=get_executive_model(),
            description="Agent for ICP generation and validation test planning.",
            instructions=[
                "You are an expert at evaluating startup viability and generating Ideal Customer Profiles (ICPs).",
                "Your objective is to generate accurate ICPs based on identified market gaps and pain points.",
                "You must output structured validation test plans to confirm viability assumptions in the real world."
            ],
            tools=[]
        )
