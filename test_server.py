import unittest
import threading
import socketserver
import http.client
from server import WorkflowHandler

class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        socketserver.TCPServer.allow_reuse_address = True
        # Use port 0 to allow the OS to assign an available ephemeral port
        cls.server = socketserver.TCPServer(("", 0), WorkflowHandler)
        cls.port = cls.server.server_address[1]

        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def test_do_GET_missing_route(self):
        """Test that missing non-API routes return 404 from SimpleHTTPRequestHandler."""
        conn = http.client.HTTPConnection("localhost", self.port)
        conn.request("GET", "/non-existent-file-123.html")
        response = conn.getresponse()
        self.assertEqual(response.status, 404)
        conn.close()

if __name__ == '__main__':
    unittest.main()
