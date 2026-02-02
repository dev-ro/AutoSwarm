
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb.lance_db import LanceDb
from agno.knowledge.embedder.google import GeminiEmbedder
import os

def get_knowledge_base() -> Knowledge:
    """
    Returns a configured Knowledge object using LanceDB.
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
        embedder=GeminiEmbedder(api_key=api_key, id="models/embedding-001")
    )
    
    # Create Knowledge Base
    knowledge = Knowledge(
        vector_db=vector_db,
        # We can add default docs here if we wanted
        # num_documents=3 # default retrieval count
    )
    
    return knowledge
