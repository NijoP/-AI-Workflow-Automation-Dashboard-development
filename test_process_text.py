import unittest
from unittest.mock import patch, MagicMock
import json
import time

from process_text import process_workflow

class TestProcessText(unittest.TestCase):

    @patch('process_text.sqlite3.connect')
    def test_process_workflow_not_found(self, mock_connect):
        # Setup mock db
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Cursor fetchone returns None for not found
        mock_cursor.fetchone.return_value = None

        # Execute
        result = process_workflow('missing_id')

        # Assertions
        self.assertIsNone(result)
        mock_cursor.execute.assert_called_once_with('SELECT raw_text FROM workflows WHERE workflow_id = ?', ('missing_id',))

    @patch('process_text.time.time')
    @patch('process_text.subprocess.Popen')
    @patch('process_text.sqlite3.connect')
    def test_process_workflow_happy_path(self, mock_connect, mock_popen, mock_time):
        # Setup mock time
        mock_time.side_effect = [1000.0, 1002.5] # start_time and end_time, diff = 2.5s = 2500ms

        # Setup mock db
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        raw_text_data = "This is an urgent test report that is longer than fifty characters to test the summary logic."
        mock_cursor.fetchone.return_value = (raw_text_data,)

        # Setup mock subprocess
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        mock_tasks = [
            "Submit report",
            "Urgent meeting",
            "Routine check"
        ]
        mock_tasks_json = json.dumps(mock_tasks).encode('utf-8')
        mock_process.communicate.return_value = (mock_tasks_json, b"")

        # Execute
        result = process_workflow('workflow_123')

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['workflow_id'], 'workflow_123')
        self.assertTrue(result['summary'].startswith(f"Processed input of {len(raw_text_data)} characters. Primary focus: "))
        self.assertEqual(result['tasks'], mock_tasks)
        self.assertEqual(result['priority_items'], ["Submit report", "Urgent meeting"])
        self.assertEqual(result['processing_time_ms'], 2500.0)

        # Check DB update was called
        mock_cursor.execute.assert_called_with('''
        UPDATE workflows
        SET summary = ?, tasks = ?, priority_items = ?, processing_time_ms = ?, status = ?
        WHERE workflow_id = ?
    ''', (result['summary'], json.dumps(mock_tasks), json.dumps(result['priority_items']), 2500.0, 'COMPLETED', 'workflow_123'))

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
