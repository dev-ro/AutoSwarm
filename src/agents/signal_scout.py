from agno.agent import Agent
from src.core.models import get_executive_model # Type: ignore

class SignalScoutAgent(Agent):
    def __init__(self, name: str = "Signal Scout"):
        super().__init__(
            model=get_executive_model(),
            description="Agent for pain-point extraction from social and forum data.",
            instructions=[
                "You are an expert at analyzing social and forum data to find market gaps.",
                "Your objective is high-density pain-point extraction from user discussions.",
                "Output structured summaries of repetitive complaints or unmet needs."
            ],
            tools=[]
        )
