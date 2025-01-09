#!/usr/bin/env python3

import unittest
import http.client
import json
import threading
import time
from datetime import datetime
from server import run_server
from database import ChatDatabase
import os
import sqlite3
import shutil

class TestChatEndpoints(unittest.TestCase):
    """Test cases for chat server endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment before all tests"""
        # Set up database path
        cls.db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_database")
        cls.db_path = os.path.join(cls.db_dir, "chat.db")
        
        # Create database directory if it doesn't exist
        os.makedirs(cls.db_dir, exist_ok=True)
        
        # Start server in a separate thread
        cls.server_thread = threading.Thread(target=lambda: run_server(db_path=cls.db_path))
        cls.server_thread.daemon = True
        print("Starting server...")
        cls.server_thread.start()
        time.sleep(1)  # Wait for server to start
        
        # Create HTTP connection
        cls.conn = http.client.HTTPConnection("localhost", 8000)
        
        # Initialize database
        cls.db = ChatDatabase(cls.db_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.conn.close()
        cls.db.close()
        # Remove test database directory
        if os.path.exists(cls.db_dir):
            shutil.rmtree(cls.db_dir)
    
    def setUp(self):
        """Set up before each test"""
        # Clear all messages from database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages")
            conn.commit()
    
    def test_get_empty_messages(self):
        """Test GET /api/messages with empty database"""
        print("\nTest: GET /api/messages (empty database)")
        self.conn.request("GET", "/api/messages")
        response = self.conn.getresponse()
        
        # Check response status
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, "OK")
        
        # Check response content
        data = json.loads(response.read().decode())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
        
        print("- Empty messages test passed")
    
    def test_post_and_get_message(self):
        """Test POST and GET /api/messages with a single message"""
        print("\nTest: POST and GET /api/messages (single message)")
        
        # Test message data
        message = {
            "content": "Test message from test_endpoints.py"
        }
        
        # Send POST request
        headers = {'Content-type': 'application/json'}
        self.conn.request(
            "POST",
            "/api/messages",
            json.dumps(message),
            headers
        )
        response = self.conn.getresponse()
        
        # Check POST response
        self.assertEqual(response.status, 201)
        post_data = json.loads(response.read().decode())
        self.assertEqual(post_data['status'], 'success')
        self.assertEqual(post_data['message']['content'], message['content'])
        
        # Get message ID from response
        message_id = post_data['message']['id']
        
        # Send GET request
        self.conn.request("GET", "/api/messages")
        response = self.conn.getresponse()
        
        # Check GET response
        self.assertEqual(response.status, 200)
        get_data = json.loads(response.read().decode())
        
        # Verify message content
        self.assertEqual(len(get_data), 1)
        self.assertEqual(get_data[0]['id'], message_id)
        self.assertEqual(get_data[0]['content'], message['content'])
        
        print("- Post and get message test passed")
    
    def test_multiple_messages(self):
        """Test POST and GET with multiple messages"""
        print("\nTest: Multiple messages")
        
        # Post multiple messages
        messages = [
            {"content": f"Test message {i}"} for i in range(3)
        ]
        
        headers = {'Content-type': 'application/json'}
        for msg in messages:
            self.conn.request(
                "POST",
                "/api/messages",
                json.dumps(msg),
                headers
            )
            response = self.conn.getresponse()
            self.assertEqual(response.status, 201)
            response.read()  # Clear the response
        
        # Get all messages
        self.conn.request("GET", "/api/messages")
        response = self.conn.getresponse()
        
        # Check response
        self.assertEqual(response.status, 200)
        data = json.loads(response.read().decode())
        
        # Verify messages
        self.assertEqual(len(data), len(messages))
        for i, msg in enumerate(reversed(messages)):  # Reversed because newest first
            self.assertEqual(data[i]['content'], msg['content'])
        
        print("- Multiple messages test passed")
    
    def test_invalid_message(self):
        """Test POST with invalid message format"""
        print("\nTest: Invalid message format")
        
        # Test cases for invalid messages
        invalid_messages = [
            {},  # Empty message
            {"content": ""},  # Empty content
            {"content": "    "},  # Only whitespace
            {"wrong_field": "test"}  # Missing content field
        ]
        
        headers = {'Content-type': 'application/json'}
        for msg in invalid_messages:
            self.conn.request(
                "POST",
                "/api/messages",
                json.dumps(msg),
                headers
            )
            response = self.conn.getresponse()
            
            # Should get 400 Bad Request
            self.assertEqual(response.status, 400)
            response.read()  # Clear the response
        
        print("- Invalid message test passed")

def run_tests():
    """Run all tests"""
    print("Starting chat endpoint tests...")
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == "__main__":
    run_tests()
