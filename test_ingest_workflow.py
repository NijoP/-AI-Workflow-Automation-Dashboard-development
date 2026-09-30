import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import uuid
import datetime
from ingest_workflow import ingest

class TestIngestWorkflow(unittest.TestCase):
    def setUp(self):
        # Create an in-memory database for testing
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

        # Create the table as expected by the application
        self.cursor.execute('''
            CREATE TABLE workflows (
                workflow_id TEXT PRIMARY KEY,
                raw_text TEXT,
                summary TEXT,
                tasks TEXT,
                priority_items TEXT,
                processing_time_ms REAL,
                status TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_ingest_success(self):
        # Instead of returning the raw connection which gets closed by ingest(),
        # let's mock it using patch with a MagicMock that wraps our connection

        # Create a mock connection that behaves like our in-memory connection
        # but ignores the close() call
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = self.conn.cursor()

        # We need to make commit() actually commit our in-memory DB if needed,
        # but since we share the connection, the changes are visible to us immediately.
        # We can just let commit do nothing or pass it through.
        mock_conn.commit.side_effect = self.conn.commit
        mock_conn.close.return_value = None

        with patch('ingest_workflow.sqlite3.connect', return_value=mock_conn):
            raw_text = "Test raw text for workflow."

            # Call the function
            workflow_id = ingest(raw_text)

            # Verify it returns an 8-character string (as per str(uuid.uuid4())[:8])
            self.assertEqual(len(workflow_id), 8)

            # Verify the data was inserted correctly
            self.cursor.execute("SELECT workflow_id, raw_text, status FROM workflows WHERE workflow_id=?", (workflow_id,))
            row = self.cursor.fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[0], workflow_id)
            self.assertEqual(row[1], raw_text)
            self.assertEqual(row[2], 'PENDING')

            # Verify close was called on the mock
            mock_conn.close.assert_called_once()
            mock_conn.commit.assert_called_once()

    def test_ingest_database_error(self):
        # Simulate a database error on connect
        with patch('ingest_workflow.sqlite3.connect', side_effect=sqlite3.OperationalError("Database is locked")):
            raw_text = "Test raw text for error."

            # Verify that the exception propagates
            with self.assertRaises(sqlite3.OperationalError):
                ingest(raw_text)

if __name__ == '__main__':
    unittest.main()
