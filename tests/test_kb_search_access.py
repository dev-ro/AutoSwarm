
import threading
import time
from dotenv import load_dotenv
load_dotenv()

from src.core.knowledge import get_knowledge_base

def concurrent_search(kb, thread_id):
    try:
        print(f"Thread {thread_id}: Starting search...")
        # Simple search query to trigger index read
        results = kb.vector_db.search(query="test query")
        print(f"Thread {thread_id}: Search successful, found {len(results)} results.")
    except Exception as e:
        print(f"Thread {thread_id}: [ERROR]: {e}")
        # Identify OS Error 5 (Access Denied) or similar locking issues
        if "os error 5" in str(e).lower() or "permission denied" in str(e).lower():
            print(f"Thread {thread_id}: Detected file locking collision!")

def test_kb_concurrency():
    print("Initializing Knowledge Base...")
    kb = get_knowledge_base()
    
    threads = []
    num_threads = 5 # Simulating multiple concurrent search requests
    
    print(f"Launching {num_threads} concurrent search threads...")
    for i in range(num_threads):
        t = threading.Thread(target=concurrent_search, args=(kb, i))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("\nKB Concurrency Test Complete.")

if __name__ == "__main__":
    test_kb_concurrency()
