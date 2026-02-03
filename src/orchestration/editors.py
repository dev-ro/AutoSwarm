from .state import AgentState
import abc
from agno.agent import Agent
from src.core.models import get_executive_model, MockGemini

class BaseEditor(abc.ABC):
    def __init__(self):
        self.model = get_executive_model()

    def generate_feedback(self, state: AgentState, genre_label: str) -> str:
        persona = state.get('selected_persona')
        constitution = state.get('genre_constitution')
        manuscript = state.get('input_text', "")
        
        if not persona:
            return "Error: No persona selected for editing."

        # Construct a robust system prompt integrating all components
        system_instructions = [
            f"IDENTITY: You are {persona.name}.",
            f"CORE VOICE/TONE: {persona.system_prompt_template}",
            f"GENRE CONSTITUTION ({genre_label}):",
            constitution if constitution else "Follow general high-quality writing principles for this genre.",
            "STYLE CONSTRAINTS:",
            f"- Verbosity (1-5): {persona.verbosity}",
            f"- Critique Harshness (1-5): {persona.critique_harshness}",
            "TASK:",
            f"Analyze the manuscript provided below as a {genre_label} editor.",
            "Provide specific, actionable feedback based on your persona and the genre constitution."
        ]
        
        # Check if we are using the MockGemini
        if isinstance(self.model, MockGemini):
            # Bypass agno.Agent for mock
            full_prompt = "\n".join(system_instructions) + "\n\nMANUSCRIPT:\n" + manuscript
            response = self.model.run(full_prompt)
            return response.content

        agent = Agent(
            model=self.model,
            instructions=system_instructions,
            markdown=True
        )
        
        try:
            # Execute the generation
            response = agent.run(manuscript)
            # Return the content of the response
            if hasattr(response, 'content'):
                return response.content
            return str(response)
        except Exception as e:
            # Fallback for errors
            return f"Error during live LLM generation: {str(e)}"

    @abc.abstractmethod
    def process(self, state: AgentState) -> AgentState:
        pass

class SciFiEditor(BaseEditor):
    def process(self, state: AgentState) -> AgentState:
        persona_name = state['selected_persona'].name if state['selected_persona'] else "Unknown"
        print(f"--- Sci-Fi Editor Processing using Persona: {persona_name} ---")
        state['editor_output'] = self.generate_feedback(state, "Sci-Fi")
        state['next_node'] = "END"
        return state

class NoirEditor(BaseEditor):
    def process(self, state: AgentState) -> AgentState:
        persona_name = state['selected_persona'].name if state['selected_persona'] else "Unknown"
        print(f"--- Noir Editor Processing using Persona: {persona_name} ---")
        state['editor_output'] = self.generate_feedback(state, "Noir")
        state['next_node'] = "END"
        return state

class FantasyEditor(BaseEditor):
    def process(self, state: AgentState) -> AgentState:
        persona_name = state['selected_persona'].name if state['selected_persona'] else "Unknown"
        print(f"--- Fantasy Editor Processing using Persona: {persona_name} ---")
        state['editor_output'] = self.generate_feedback(state, "Fantasy")
        state['next_node'] = "END"
        return state

class AcademicEditor(BaseEditor):
    def process(self, state: AgentState) -> AgentState:
        persona_name = state['selected_persona'].name if state['selected_persona'] else "Unknown"
        print(f"--- Academic Editor Processing using Persona: {persona_name} ---")
        state['editor_output'] = self.generate_feedback(state, "Academic")
        state['next_node'] = "END"
        return state

class GenericEditor(BaseEditor):
    def process(self, state: AgentState) -> AgentState:
        persona_name = state['selected_persona'].name if state['selected_persona'] else "Unknown"
        print(f"--- Generic Editor Processing using Persona: {persona_name} ---")
        state['editor_output'] = self.generate_feedback(state, "General Fiction")
        state['next_node'] = "END"
        return state
