import unittest
import sys
import os

def run_tests():
    # Add current directory to sys.path to allow imports of PersonaEngine
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    run_tests()