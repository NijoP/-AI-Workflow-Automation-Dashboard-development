import unittest
from unittest.mock import patch, MagicMock
from init_db import init_db

class TestInitDb(unittest.TestCase):
    @patch('init_db.sqlite3.connect')
    def test_init_db(self, mock_connect):
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Act
        init_db()

        # Assert
        mock_connect.assert_called_once_with('workflow_engine.db')
        mock_conn.cursor.assert_called_once()

        # Verify the execute call contains the CREATE TABLE statement
        mock_cursor.execute.assert_called_once()
        executed_sql = mock_cursor.execute.call_args[0][0]

        self.assertIn("CREATE TABLE IF NOT EXISTS workflows", executed_sql)
        self.assertIn("workflow_id TEXT PRIMARY KEY", executed_sql)
        self.assertIn("raw_text TEXT", executed_sql)
        self.assertIn("summary TEXT", executed_sql)
        self.assertIn("tasks TEXT", executed_sql)
        self.assertIn("priority_items TEXT", executed_sql)
        self.assertIn("processing_time_ms REAL", executed_sql)
        self.assertIn("status TEXT", executed_sql)
        self.assertIn("timestamp TEXT", executed_sql)

        # Verify commit and close
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
