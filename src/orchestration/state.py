from typing import TypedDict, Optional, List, Dict, Any
from src.personality.schemas import Persona, NLUClassification

class AgentState(TypedDict):
    # Input
    input_text: str
    
    # Processed Data
    classification: Optional[NLUClassification]
    selected_persona: Optional[Persona]
    genre_constitution: Optional[str]
    
    # Output
    editor_output: Optional[str]
    critique_points: Optional[List[str]]
    
    # Metadata / Control
    next_node: str
    history: List[Dict[str, Any]]
