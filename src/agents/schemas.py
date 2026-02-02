
from pydantic import BaseModel, Field
from typing import List

class Task(BaseModel):
    description: str = Field(..., description="Description of the task to be performed.")
    assigned_agent: str = Field(..., description="The type of agent assigned to this task (e.g., 'Researcher', 'Coder', 'Reviewer').")

class Plan(BaseModel):
    goal: str = Field(..., description="The overall goal of the plan.")
    steps: List[Task] = Field(..., description="List of actionable tasks to execute the plan.")
