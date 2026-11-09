import http.server
import socketserver
import json
import os
import sys

PORT = 8080
SAVE_FILE = 'save_data.json'

class SaveHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/save':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            # Disable caching
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = f.read()
            else:
                data = '{}'
            self.wfile.write(data.encode('utf-8'))
        elif self.path == '/api/times':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            
            time_file = 'time_data.json'
            if os.path.exists(time_file):
                with open(time_file, 'r', encoding='utf-8') as f:
                    data = f.read()
            else:
                data = '{}'
            self.wfile.write(data.encode('utf-8'))
        else:
            # Force cache refresh for html files during dev
            super().do_GET()
            
    def end_headers(self):
        if self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()
            
    def do_POST(self):
        if self.path in ('/api/save', '/api/times'):
            content_length_str = self.headers.get('Content-Length')
            if not content_length_str:
                self.send_error(411, "Length Required")
                return
            
            content_length = int(content_length_str)
            if content_length > 1024 * 1024:  # 1MB limit
                self.send_error(413, "Payload Too Large")
                return
                
            post_data = self.rfile.read(content_length)
            
            try:
                new_data = json.loads(post_data.decode('utf-8'))
                if not isinstance(new_data, dict):
                    raise ValueError("Payload must be a JSON object")
                
                if self.path == '/api/save':
                    target_file = SAVE_FILE
                    # Merge logic for save_data
                    file_data = {}
                    if os.path.exists(target_file):
                        with open(target_file, 'r', encoding='utf-8') as f:
                            file_data = json.load(f)
                    
                    file_data.update(new_data)
                else:
                    target_file = 'time_data.json'
                    # Merge logic for time_data (take max)
                    file_data = {}
                    if os.path.exists(target_file):
                        with open(target_file, 'r', encoding='utf-8') as f:
                            file_data = json.load(f)
                            
                    for k, v in new_data.items():
                        if not isinstance(v, (int, float)): continue
                        if k not in file_data or v > file_data[k]:
                            file_data[k] = v
                
                # Atomic write
                tmp_file = target_file + '.tmp'
                with open(tmp_file, 'w', encoding='utf-8') as f:
                    json.dump(file_data, f, ensure_ascii=False)
                os.replace(tmp_file, target_file)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# To allow reusing the port if restarting quickly
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), SaveHandler) as httpd:
    print(f"Serving at port {PORT} with Save API")
    httpd.serve_forever()
