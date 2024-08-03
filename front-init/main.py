import http.server
import socketserver
import os
import socket
import multiprocessing
import json
from datetime import datetime

PORT = 3000
SOCKET_PORT = 5000
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'
DATA_FILE_PATH = '/usr/src/app/storage/data.json'

# Simple HTTP Request Handler
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/message':
            self.path = '/message.html'
        elif self.path.startswith('/static/'):
            self.path = self.path
        else:
            self.path = '/error.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = post_data.decode('utf-8')
            post_data = dict(x.split('=') for x in post_data.split('&'))
            
            # Send data to socket server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', SOCKET_PORT))
                s.sendall(json.dumps(post_data).encode('utf-8'))
                s.close()

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

# Socket server for handling form data and saving to JSON file
def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', SOCKET_PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode('utf-8'))
                message['date'] = str(datetime.now())
                save_to_json(message)

def save_to_json(data):
    file_path = DATA_FILE_PATH
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Read existing data
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    # Append new data
    existing_data.append(data)
    # Write updated data
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

def start_http_server():
    os.chdir('templates')
    handler = SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Serving HTTP on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Start HTTP server and socket server in separate processes
    http_process = multiprocessing.Process(target=start_http_server)
    socket_process = multiprocessing.Process(target=socket_server)
    
    http_process.start()
    socket_process.start()
    
    http_process.join()
    socket_process.join()
