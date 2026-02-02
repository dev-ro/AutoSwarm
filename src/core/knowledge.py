import os
from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.search import SearchType

def get_knowledge_base() -> Knowledge:
    """
    Returns the persistent Knowledge Base backed by LanceDB.
    """
    db_path = "data/knowledge_base"
    os.makedirs(db_path, exist_ok=True)

    # Configure the LanceDB vector database
    vector_db = LanceDb(
        table_name="research_knowledge",
        uri=db_path,
        search_type=SearchType.keyword,
        embedder=GeminiEmbedder(id="models/embedding-001") 
    )

    # Initialize the Knowledge Base
    knowledge_base = Knowledge(
        vector_db=vector_db,
    )
    
    # Ensure the vector_db is created if it doesn't exist.
    if not vector_db.exists():
        vector_db.create()

    return knowledge_base
