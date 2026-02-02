
from agno.knowledge import AgentKnowledge
from agno.vectordb.lancedb import LanceDb
from agno.embedder.google import GeminiEmbedder
import os

def get_knowledge_base() -> AgentKnowledge:
    """
    Returns a configured AgentKnowledge object using LanceDB.
    """
    # Ensure the knowledge directory exists
    db_path = "./workspace/knowledge"
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    
    # We use Google's Gemini Embedder since we have the key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Initialize Vector DB
    vector_db = LanceDb(
        table_name="research_knowledge",
        uri=db_path,
        embedder=GeminiEmbedder(api_key=api_key, model="models/embedding-001")
    )
    
    # Create Knowledge Base
    knowledge = AgentKnowledge(
        vector_db=vector_db,
        # We can add default docs here if we wanted
        # num_documents=3 # default retrieval count
    )
    
    return knowledge
