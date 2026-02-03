from src.core.knowledge import get_knowledge_base

try:
    kb = get_knowledge_base()
    print("KB created successfully")
    print(f"Vector DB type: {type(kb.vector_db)}")
    print(f"Vector DB dir: {dir(kb.vector_db)}")
    
    # Try to access table
    if hasattr(kb.vector_db, 'table'):
        print(f"Has 'table' attribute: {kb.vector_db.table}")
    else:
        print("No 'table' attribute")
        
except Exception as e:
    print(f"Error: {e}")
