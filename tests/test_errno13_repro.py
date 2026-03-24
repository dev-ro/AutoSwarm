
import unittest
from pathlib import Path
from src.agents.researcher import SafeFileTools

class TestErrno13(unittest.TestCase):
    def setUp(self):
        self.workspace = Path("workspace")
        self.directory = self.workspace / "ArchitecturalTrends2026"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.file_tools = SafeFileTools(base_dir=self.workspace)

    def test_read_directory_graceful_error(self):
        """SafeFileTools.read_file SHOULD return an error message for a directory."""
        result = self.file_tools.read_file("ArchitecturalTrends2026")
        print(f"Result: {result}")
        self.assertIn("is a directory", result)

if __name__ == "__main__":
    unittest.main()
