#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
from http import HTTPStatus
from datetime import datetime

class ChatRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for our chat application"""

    def __init__(self, *args, **kwargs):
        # Set the directory containing static files
        self.static_dir = os.path.join(os.path.dirname(__file__), 'static')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Route handling
        if parsed_path.path == '/':
            self.serve_file('templates/index.html', 'text/html')
        elif parsed_path.path == '/login':
            self.serve_file('templates/login.html', 'text/html')
        elif parsed_path.path.startswith('/static/'):
            # Serve static files (CSS, JS)
            self.serve_static_file(parsed_path.path[8:])  # Remove '/static/' prefix
        elif parsed_path.path == '/api/messages':
            self.send_messages()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Resource not found")

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        # Get the content length to read the body
        content_length = int(self.headers.get('Content-Length', 0))
        
        if parsed_path.path == '/api/messages':
            # Read and parse the request body
            post_data = self.rfile.read(content_length)
            try:
                message_data = json.loads(post_data.decode('utf-8'))
                self.handle_new_message(message_data)
            except json.JSONDecodeError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON data")
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Resource not found")

    def serve_file(self, relative_path, content_type):
        """Serve a file with the specified content type"""
        try:
            with open(os.path.join(os.path.dirname(__file__), relative_path), 'rb') as f:
                content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")

    def serve_static_file(self, file_path):
        """Serve static files with appropriate content types"""
        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.gif': 'image/gif'
        }
        
        file_ext = os.path.splitext(file_path)[1]
        content_type = content_types.get(file_ext, 'application/octet-stream')
        
        try:
            with open(os.path.join(self.static_dir, file_path), 'rb') as f:
                content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND, "Static file not found")

    def send_messages(self):
        """Send message history as JSON response"""
        # Placeholder for message retrieval logic
        messages = []  # This will be replaced with actual message fetching
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(messages).encode('utf-8'))

    def handle_new_message(self, message_data):
        """Handle new message submission"""
        # Validate message data
        if 'content' not in message_data or not message_data['content'].strip():
            self.send_error(HTTPStatus.BAD_REQUEST, "Message content is required")
            return

        # Add timestamp to message
        message_data['timestamp'] = datetime.now().isoformat()
        
        # Placeholder for message storage logic
        # This will be implemented later with Git and SQLite integration
        
        # Send success response
        self.send_response(HTTPStatus.CREATED)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))

def run_server(port=8000):
    """Start the HTTP server"""
    with socketserver.TCPServer(("", port), ChatRequestHandler) as httpd:
        print(f"Server running on port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
