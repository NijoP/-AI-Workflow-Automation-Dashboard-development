import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import health_check

class TestHealthCheck(unittest.TestCase):

    @patch('health_check.sqlite3.connect')
    @patch('health_check.os.path.exists')
    def test_all_exists(self, mock_exists, mock_connect):
        mock_exists.return_value = True

        # Setup mock for sqlite
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [42]

        captured_output = io.StringIO()
        with patch('sys.stdout', new=captured_output):
            health_check.check()

        output = captured_output.getvalue()
        self.assertIn("Database status: OK", output)
        self.assertIn("Total workflows: 42", output)
        self.assertIn("Script ingest_workflow.py: OK", output)
        self.assertIn("Script process_text.py: OK", output)
        self.assertIn("Script extract_tasks.py: OK", output)

        mock_connect.assert_called_once_with('workflow_engine.db')
        mock_cursor.execute.assert_called_once_with('SELECT COUNT(*) FROM workflows')

    @patch('health_check.sqlite3.connect')
    @patch('health_check.os.path.exists')
    def test_all_missing(self, mock_exists, mock_connect):
        mock_exists.return_value = False

        captured_output = io.StringIO()
        with patch('sys.stdout', new=captured_output):
            health_check.check()

        output = captured_output.getvalue()
        self.assertIn("Database status: MISSING", output)
        self.assertNotIn("Total workflows", output)
        self.assertIn("Script ingest_workflow.py: MISSING", output)
        self.assertIn("Script process_text.py: MISSING", output)
        self.assertIn("Script extract_tasks.py: MISSING", output)

        mock_connect.assert_not_called()

    @patch('health_check.sqlite3.connect')
    @patch('health_check.os.path.exists')
    def test_partial_missing(self, mock_exists, mock_connect):
        # Database exists, some scripts missing
        def exists_side_effect(path):
            if path == 'workflow_engine.db':
                return True
            elif path == 'process_text.py':
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        # Setup mock for sqlite
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [10]

        captured_output = io.StringIO()
        with patch('sys.stdout', new=captured_output):
            health_check.check()

        output = captured_output.getvalue()
        self.assertIn("Database status: OK", output)
        self.assertIn("Total workflows: 10", output)
        self.assertIn("Script ingest_workflow.py: MISSING", output)
        self.assertIn("Script process_text.py: OK", output)
        self.assertIn("Script extract_tasks.py: MISSING", output)

if __name__ == '__main__':
    unittest.main()
