import unittest
from unittest.mock import MagicMock, patch
import json
import io
from server import WorkflowHandler

class MockHandler(WorkflowHandler):
    def __init__(self):
        # Setup mock I/O streams and state instead of calling super().__init__
        self.rfile = MagicMock()
        self.wfile = MagicMock()
        self.headers = {}
        self.path = ""
        self.client_address = ('127.0.0.1', 8000)
        self.server = MagicMock()

    # Mock the response methods
    def send_response(self, code, message=None):
        self.response_code = code

    def send_header(self, keyword, value):
        if not hasattr(self, 'sent_headers'):
            self.sent_headers = {}
        self.sent_headers[keyword] = value

    def end_headers(self):
        self.headers_ended = True


class TestWorkflowHandler(unittest.TestCase):
    def setUp(self):
        self.handler = MockHandler()

    @patch('sqlite3.connect')
    def test_do_GET_api_workflows(self, mock_connect):
        self.handler.path = '/api/workflows'

        # Setup mock db
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock row data
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'test workflow', 'timestamp': '2023-01-01'}]

        # Call do_GET
        self.handler.do_GET()

        # Verify db interaction
        mock_connect.assert_called_once_with('workflow_engine.db')
        mock_cursor.execute.assert_called_once_with('SELECT * FROM workflows ORDER BY timestamp DESC')
        mock_conn.close.assert_called_once()

        # Verify response
        self.assertEqual(self.handler.response_code, 200)
        self.assertEqual(self.handler.sent_headers.get('Content-type'), 'application/json')
        self.assertTrue(self.handler.headers_ended)

        # Verify written data
        self.handler.wfile.write.assert_called_once()
        written_data = self.handler.wfile.write.call_args[0][0]
        parsed_data = json.loads(written_data.decode())
        self.assertEqual(parsed_data, [{'id': 1, 'name': 'test workflow', 'timestamp': '2023-01-01'}])

    @patch('http.server.SimpleHTTPRequestHandler.do_GET')
    def test_do_GET_other_path(self, mock_super_do_GET):
        self.handler.path = '/other/path'

        self.handler.do_GET()

        mock_super_do_GET.assert_called_once()

    @patch('subprocess.run')
    @patch('subprocess.Popen')
    def test_do_POST_api_ingest(self, mock_popen, mock_run):
        self.handler.path = '/api/ingest'

        # Setup request data
        test_payload = {"raw_text": "Sample workflow text"}
        payload_bytes = json.dumps(test_payload).encode()
        self.handler.headers = {'Content-Length': str(len(payload_bytes))}
        self.handler.rfile.read.return_value = payload_bytes

        # Setup Popen mock to return dummy workflow_id
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"Workflow 12345 ingested", b"")
        mock_popen.return_value = mock_process

        # Call do_POST
        self.handler.do_POST()

        # Verify Popen called with correct arguments
        import subprocess
        mock_popen.assert_called_once_with(['python3', 'ingest_workflow.py', 'Sample workflow text'], stdout=subprocess.PIPE)

        # Verify run called with correct arguments
        mock_run.assert_called_once_with(['python3', 'process_text.py', '12345'])

        # Verify response
        self.assertEqual(self.handler.response_code, 200)
        self.assertEqual(self.handler.sent_headers.get('Content-type'), 'application/json')
        self.assertTrue(self.handler.headers_ended)

        # Verify written data
        self.handler.wfile.write.assert_called_once()
        written_data = self.handler.wfile.write.call_args[0][0]
        parsed_data = json.loads(written_data.decode())
        self.assertEqual(parsed_data, {"status": "success", "workflow_id": "12345"})

if __name__ == '__main__':
    unittest.main()
