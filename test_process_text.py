import unittest
from unittest.mock import patch, MagicMock
from process_text import process_workflow

class TestProcessText(unittest.TestCase):

    @patch('process_text.sqlite3.connect')
    def test_process_workflow_not_found(self, mock_connect):
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Configure the mock connection to return our mock cursor
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Configure fetchone to return None, simulating 'workflow not found'
        mock_cursor.fetchone.return_value = None

        # Act
        result = process_workflow("non_existent_id")

        # Assert
        self.assertIsNone(result)
        mock_connect.assert_called_once_with('workflow_engine.db')
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with('SELECT raw_text FROM workflows WHERE workflow_id = ?', ("non_existent_id",))
        mock_cursor.fetchone.assert_called_once()

        # Verify that we didn't do any further operations like update or commit
        self.assertEqual(mock_cursor.execute.call_count, 1) # Only the SELECT query
        mock_conn.commit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
