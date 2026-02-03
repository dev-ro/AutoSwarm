import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import io

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.researcher import verify_knowledge
from src.agents.manager import Manager
from src.agents.schemas import Task, AgentType

class TestAutoArchival(unittest.TestCase):

    @patch('src.agents.researcher.get_knowledge_base')
    def test_verify_knowledge(self, mock_get_kb):
        """Test that verify_knowledge correctly counts documents."""
        print("\n>>> Testing verify_knowledge...")
        
        # Setup mock KB and Table
        mock_kb = MagicMock()
        mock_table = MagicMock()
        mock_df = MagicMock()
        
        mock_get_kb.return_value = mock_kb
        mock_kb.vector_db.exists.return_value = True
        mock_kb.vector_db.get_table.return_value = mock_table
        # Simulate table.to_pandas() returning a list/dataframe with length 5
        mock_table.to_pandas.return_value = [1, 2, 3, 4, 5]
        
        count = verify_knowledge()
        
        self.assertEqual(count, 5)
        print("✅ verify_knowledge returned correct count (5).")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('src.agents.manager.verify_knowledge')
    @patch('src.agents.manager.get_research_agent')
    def test_memory_leak_detection(self, mock_get_agent, mock_verify_knowledge, mock_stdout):
        """Test Manager detects memory leak when artifacts > 0 but KB delta == 0."""
        print("\n>>> Testing Memory Leak Detection...")
        
        # Setup Manager
        manager = Manager()
        manager.state_manager = MagicMock()
        
        # Setup Agent
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_agent.run.return_value = MagicMock(content="Found some info: - Item 1\n- Item 2")
        
        # Scenario: Leak
        # Pre-task count = 10
        # Post-task count = 10 (Delta = 0)
        # Artifact count = 5
        mock_verify_knowledge.side_effect = [10, 10] 
        manager.state_manager.get_artifact_count.return_value = 5
        
        task = Task(description="Research logic", assigned_agent=AgentType.RESEARCHER)
        
        manager.delegate_task(task, "prompt", task_id=123)
        
        output = mock_stdout.getvalue()
        
        if "[WARNING] Memory Leak Detected" in output:
            print("✅ Memory Leak correctly detected.")
        else:
            print("❌ FAILED: Memory Leak warning not found.")
            print(f"Captured Output:\n{output}")
            self.fail("Memory Leak warning not found")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('src.agents.manager.verify_knowledge')
    @patch('src.agents.manager.get_research_agent')
    def test_successful_save_detection(self, mock_get_agent, mock_verify_knowledge, mock_stdout):
        """Test Manager acknowledges successful save when KB delta > 0."""
        print("\n>>> Testing Successful Save Detection...")
        
        manager = Manager()
        manager.state_manager = MagicMock()
        
        mock_agent = MagicMock()
        mock_get_agent.return_value = mock_agent
        mock_agent.run.return_value = MagicMock(content="Found info.")
        
        # Scenario: Success
        # Pre-task count = 10
        # Post-task count = 12 (Delta = 2)
        mock_verify_knowledge.side_effect = [10, 12] 
        manager.state_manager.get_artifact_count.return_value = 5
        
        task = Task(description="Research logic", assigned_agent=AgentType.RESEARCHER)
        
        manager.delegate_task(task, "prompt", task_id=124)
        
        output = mock_stdout.getvalue()
        
        if "Knowledge Base grew by 2 documents" in output:
             print("✅ Successful save correctly detected.")
        else:
            print("❌ FAILED: Success message not found.")
            print(f"Captured Output:\n{output}")
            self.fail("Success message not found")

if __name__ == '__main__':
    unittest.main()
