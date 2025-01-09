#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
from http import HTTPStatus
from datetime import datetime
from database import ChatDatabase
from multi_repo_handler import MultiRepoHandler

class ChatRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for our chat application"""

    def __init__(self, *args, **kwargs):
        # Initialize database and git handlers
        self.db = ChatDatabase()
        self.git = MultiRepoHandler()
        
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
        elif parsed_path.path == '/api/repositories':
            # Add a new repository
            post_data = self.rfile.read(content_length)
            try:
                repo_data = json.loads(post_data.decode('utf-8'))
                if not all(k in repo_data for k in ['owner', 'name']):
                    self.send_error(HTTPStatus.BAD_REQUEST, "Owner and name are required")
                    return
                    
                # Add repository to database and git handler
                repo_id = self.db.add_repository(repo_data['owner'], repo_data['name'])
                self.git.add_repository(
                    owner=repo_data['owner'],
                    name=repo_data['name'],
                    branch=repo_data.get('branch', 'main'),
                    message_path=repo_data.get('message_path', 'messages')
                )
                
                # Send success response
                response_data = {
                    'status': 'success',
                    'repository': {
                        'id': repo_id,
                        'owner': repo_data['owner'],
                        'name': repo_data['name']
                    }
                }
                
                self.send_response(HTTPStatus.CREATED)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON data")
            except Exception as e:
                self.send_error(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    f"Error adding repository: {str(e)}"
                )
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
        try:
            # Get messages from database
            messages = self.db.get_messages()
            
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(messages).encode('utf-8'))
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))

    def handle_new_message(self, message_data):
        """Handle new message submission"""
        try:
            # Validate message data
            if 'content' not in message_data or not message_data['content'].strip():
                self.send_error(HTTPStatus.BAD_REQUEST, "Message content is required")
                return

            # Add timestamp to message
            timestamp = datetime.now().isoformat()
            
            # Store message in database
            message_id = self.db.add_message(
                content=message_data['content'],
                timestamp=timestamp
            )
            
            # Store message in Git repositories
            commit_hashes = self.git.store_message(
                message_content=message_data['content'],
                message_id=message_id
            )
            
            # Update database with commit hashes
            if commit_hashes:
                self.db.update_message_commits(message_id, commit_hashes)
            
            # Send success response with message details
            response_data = {
                'status': 'success',
                'message': {
                    'id': message_id,
                    'content': message_data['content'],
                    'timestamp': timestamp,
                    'repositories': commit_hashes
                }
            }
            
            self.send_response(HTTPStatus.CREATED)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            self.send_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Error storing message: {str(e)}"
            )

def run_server(port=8000, db_path="database/chat.db"):
    """Start the HTTP server"""
    class ConfiguredHandler(ChatRequestHandler):
        def __init__(self, *args, **kwargs):
            self.db = ChatDatabase(db_path)
            self.git = MultiRepoHandler()
            self.static_dir = os.path.join(os.path.dirname(__file__), 'static')
            super(ChatRequestHandler, self).__init__(*args, **kwargs)

    with socketserver.TCPServer(("", port), ConfiguredHandler) as httpd:
        print(f"Server running on port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
