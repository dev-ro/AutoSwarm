import os
from agno.agent import Agent
from src.core.models import get_executive_model

class AnalystAgent(Agent):
    def __init__(self, name: str = "Quant"):
        super().__init__(
            model=get_executive_model(),
            description="An objective cost-benefit analysis agent for architectural and logic decisions.",
            instructions=[
                "You are an expert systems architect and quantitative analyst.",
                "Your objective is to provide high-density, quantifiable cost-benefit analysis for any technical or logical decision.",
                "MANDATE: Output must strictly follow a structured format: '1. Proposal Overview', '2. Objective Pros (Quantified)', '3. Objective Cons (Quantified/Risks)', '4. ROI/Impact Projection', '5. Final Verdict (Approve/Reject/Modify)'.",
                "Do NOT use conversational filler. Be ruthless in your assessment of technical debt, cognitive complexity, and maintenance overhead.",
                "Prioritize declarative abstractions, standard git flow integrations, and CI/CD automation in your assessments."
            ],
            tools=[]
        )

if __name__ == "__main__":
    agent = AnalystAgent()
    print(agent.run("Assess the value of migrating from pip to uv for dependency management."))
