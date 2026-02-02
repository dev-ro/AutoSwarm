
from agno.agent import Agent
from src.core.models import get_executive_model
from src.tools.finance import FinanceTools

def get_finance_agent() -> Agent:
    """
    Returns the Finance Agent.
    """
    return Agent(
        model=get_executive_model(),
        description="You are a DeFi expert and portfolio manager.",
        instructions=[
            "Use 'read_balance' to check funds before any decision.",
            "Use 'evaluate_opportunity' to assess risk/reward.",
            "Use 'send_transaction' only when explicitly authorized or part of a clear plan.",
            "Be conservative with funds."
        ],
        tools=[FinanceTools()],
        markdown=True
    )
