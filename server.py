import http.server
import socketserver
import json
import sqlite3
import urllib.parse
from db_utils import get_db_connection

PORT = 8000

class WorkflowHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/workflows':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM workflows ORDER BY timestamp DESC')
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            self.wfile.write(json.dumps(rows).encode())
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path == '/api/ingest':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            import subprocess
            # Ingest
            process = subprocess.Popen(['python3', 'ingest_workflow.py', data['raw_text']], stdout=subprocess.PIPE)
            out, _ = process.communicate()
            workflow_id = out.decode().split('Workflow ')[1].split(' ingested')[0]
            
            # Process
            subprocess.run(['python3', 'process_text.py', workflow_id])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "workflow_id": workflow_id}).encode())

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), WorkflowHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
