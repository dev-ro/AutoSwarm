
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class AgentType(str, Enum):
    RESEARCHER = "researcher"
    SOCIAL = "social"
    FINANCE = "finance"
    CODER = "coder"
    REVIEWER = "reviewer"
    EXECUTIVE = "executive"
    WRITER = "writer"
    EDITOR = "editor"
    TAROT = "tarot"

class Task(BaseModel):
    description: str = Field(..., description="Description of the task to be performed.")
    assigned_agent: AgentType = Field(..., description="The type of agent assigned to this task.")
    project_context: Optional[str] = Field(None, description="The project name this task belongs to (e.g., 'TheSpiralProtocol').")

class Plan(BaseModel):
    goal: str = Field(..., description="The overall goal of the plan.")
    project_default: Optional[str] = Field(None, description="Default project name for all tasks in this plan.")
    steps: List[Task] = Field(..., description="List of actionable tasks to execute the plan.")

class PlanReview(BaseModel):
    should_modify: bool = Field(..., description="True if the plan needs modification, False otherwise.")
    new_plan: Optional[Plan] = Field(None, description="The new plan if modification is needed. Only include the REMAINING steps/tasks to be performed.")
    reasoning: str = Field(..., description="Reasoning for the decision.")

