import sys
import traceback

def main():
    try:
        import src.tools.social
        print("SUCCESS: src.tools.social imported")
    except Exception as e:
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()

if __name__ == '__main__':
    main()
