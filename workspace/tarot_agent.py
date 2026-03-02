#!/usr/bin/env python3
"""
Main entry point for the Tarot Agent System.
Provides a robust way to run tarot readings and generate reports.
"""
import sys
import os

# Ensure the current directory is in sys.path so 'tarot' and 'report_generator' can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Now that we renamed tarot/tarot.py to tarot/main.py, 
    # there is no name conflict between the package and the module.
    from tarot.main import main
except ImportError as e:
    print(f"Error: Could not import tarot module. {e}")
    # Fallback to local import if needed
    try:
        from tarot.main import main
    except ImportError:
        print("Final attempt failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()