# src/core/knowledge.py
import os
from pathlib import Path

# Use the explicitly appropriate Knowledge class for local file systems if available
from agno.knowledge import Knowledge 
from agno.vectordb.lancedb import LanceDb
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.search import SearchType

# Assuming Local/FileSystem Knowledge is utilized for the ingest loader
try:
    from agno.knowledge import FileSystemKnowledge as LocalWorkspaceKnowledge
except ImportError:
    # Fallback to standard Knowledge if Agno version dictates differently
    LocalWorkspaceKnowledge = Knowledge

def get_knowledge_base() -> LocalWorkspaceKnowledge:
    """
    Returns the persistent Knowledge Base backed by LanceDB.
    """
    # Verify OpenAI configuration
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is missing. Required for standardizing text-embedding-3-small.")

    db_path = "data/knowledge_base"
    os.makedirs(db_path, exist_ok=True)

    # Route all embeddings explicitly through the OpenAI API
    vector_db = LanceDb(
        table_name="research_knowledge",
        uri=db_path,
        search_type=SearchType.keyword,
        embedder=OpenAIEmbedder(id="text-embedding-3-small") 
    )

    # Filter to isolate local workspace reader logic to explicitly approved flat files
    approved_extensions = {".txt", ".md"}
    workspace_dir = Path("workspace")

    # Ingest file collection natively filtering out directories (prevention of errno 13)
    valid_files = [
        str(f) for f in workspace_dir.rglob("*")
        if f.is_file() and f.suffix.lower() in approved_extensions
    ] if workspace_dir.exists() else []

    # Initialize Knowledge Base targeting safe filepaths
    knowledge_base = LocalWorkspaceKnowledge(
        vector_db=vector_db,
        # Pass the vetted flat files to the reader (API varies by Agno release version)
        # document_paths=valid_files, 
    )
    
    # Store the pre-filtered safe paths to the crawler/reader instance state if manual loading is required
    knowledge_base.valid_flat_files = valid_files

    if not vector_db.exists():
        vector_db.create()

    return knowledge_base
