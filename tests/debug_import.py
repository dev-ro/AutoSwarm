import sys

def test_debug_tantivy():
    print("EXECUTABLE:", sys.executable)
    try:
        import tantivy
        print("SUCCESS")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e
