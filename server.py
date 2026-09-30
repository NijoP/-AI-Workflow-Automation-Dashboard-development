import http.server
import socketserver
import json
import sqlite3
import urllib.parse

PORT = 8000

class WorkflowHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/workflows':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            conn = sqlite3.connect('workflow_engine.db')
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

            try:
                data = json.loads(post_data.decode())
            except json.JSONDecodeError:
                self.send_error(400, "Bad Request: Invalid JSON")
                return

            if not isinstance(data, dict) or 'raw_text' not in data:
                self.send_error(400, "Bad Request: Missing 'raw_text' field")
                return

            raw_text = data['raw_text']
            if not isinstance(raw_text, str):
                self.send_error(400, "Bad Request: 'raw_text' must be a string")
                return

            # Prevent Argument list too long / large input DOS
            if len(raw_text) > 65536:
                self.send_error(413, "Payload Too Large: 'raw_text' exceeds maximum length")
                return
            
            import subprocess
            # Ingest
            process = subprocess.Popen(['python3', 'ingest_workflow.py', raw_text], stdout=subprocess.PIPE)
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
