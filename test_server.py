import unittest
from unittest.mock import patch, MagicMock
import http.server
import threading
import urllib.request
import urllib.error
import json
import socket
import os
import tempfile
import shutil

from server import WorkflowHandler

def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port

class TestWorkflowHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory and change to it
        cls.orig_dir = os.getcwd()
        cls.test_dir = tempfile.mkdtemp()
        os.chdir(cls.test_dir)

        # Create a dummy file for testing the fallback GET handler
        with open('test_dummy.html', 'w') as f:
            f.write('<html><body>Dummy</body></html>')

        cls.port = get_free_port()
        cls.server = http.server.HTTPServer(('localhost', cls.port), WorkflowHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

        # Change back to original directory and remove temporary directory
        os.chdir(cls.orig_dir)
        shutil.rmtree(cls.test_dir)

    @patch('server.sqlite3.connect')
    def test_do_GET_api_workflows(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test Workflow'}]

        url = f'http://localhost:{self.port}/api/workflows'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get('Content-type'), 'application/json')
            self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
            data = json.loads(response.read().decode())
            self.assertEqual(data, [{'id': 1, 'name': 'Test Workflow'}])

    @patch('subprocess.Popen')
    @patch('subprocess.run')
    def test_do_POST_api_ingest(self, mock_run, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'Workflow 12345 ingested', b'')
        mock_popen.return_value = mock_process

        url = f'http://localhost:{self.port}/api/ingest'
        post_data = json.dumps({"raw_text": "sample text"}).encode('utf-8')
        req = urllib.request.Request(url, data=post_data, headers={'Content-Type': 'application/json', 'Content-Length': str(len(post_data))})

        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get('Content-type'), 'application/json')
            self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
            data = json.loads(response.read().decode())
            self.assertEqual(data, {"status": "success", "workflow_id": "12345"})

        mock_popen.assert_called_once_with(['python3', 'ingest_workflow.py', 'sample text'], stdout=-1) # subprocess.PIPE is -1
        mock_run.assert_called_once_with(['python3', 'process_text.py', '12345'])

    def test_do_GET_other(self):
        # By default SimpleHTTPRequestHandler will try to serve file from current directory
        # Let's request the dummy file we created
        url = f'http://localhost:{self.port}/test_dummy.html'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            self.assertIn('text/html', response.headers.get('Content-type'))
            self.assertEqual(response.read().decode(), '<html><body>Dummy</body></html>')

        url_not_found = f'http://localhost:{self.port}/does_not_exist.html'
        req_not_found = urllib.request.Request(url_not_found)
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req_not_found)
        self.assertEqual(context.exception.code, 404)

if __name__ == '__main__':
    unittest.main()
