from pydantic import BaseModel, Field
from typing import List, Optional

class Persona(BaseModel):
    id: str = Field(..., description="Unique identifier for the persona.")
    name: str = Field(..., description="The name of the persona (e.g., 'Noir Editor').")
    genre_focus: List[str] = Field(..., description="The genres this persona specializes in.")
    verbosity: int = Field(..., ge=1, le=5, description="Verbosity scale 1-5 (1: concise, 5: flowery/detailed).")
    critique_harshness: int = Field(..., ge=1, le=5, description="Critique harshness scale 1-5 (1: gentle, 5: brutal).")
    system_prompt_template: str = Field(..., description="The base system prompt for this persona.")
    description: str = Field(..., description="Brief description of the persona.")
    target_audience: Optional[List[str]] = Field(default_factory=list, description="Target audiences this persona is best suited for.")

class NLUClassification(BaseModel):
    genre: str = Field(..., description="The identified genre of the text.")
    target_audience: str = Field(..., description="The identified target audience.")
    emotional_tone: str = Field(..., description="The identified emotional tone (e.g., 'somber', 'energetic').")
    detected_verbosity_requirement: Optional[int] = Field(None, ge=1, le=5, description="Suggested verbosity level based on input.")
    detected_harshness_requirement: Optional[int] = Field(None, ge=1, le=5, description="Suggested harshness level based on input.")
