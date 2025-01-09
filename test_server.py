#!/usr/bin/env python3

import http.client
import json
import threading
import time
from server import run_server

def test_server_response():
    """Test basic server responses"""
    # Create a connection to the server
    conn = http.client.HTTPConnection("localhost", 8000)
    
    try:
        # Test 1: Check if server responds to GET request at root
        print("\nTest 1: Testing GET /")
        conn.request("GET", "/")
        response = conn.getresponse()
        print(f"Status: {response.status} {response.reason}")
        print(f"Headers: {response.getheaders()}")
        # Clear the response body
        response.read()

        # Test 2: Check API endpoint
        print("\nTest 2: Testing GET /api/messages")
        conn.request("GET", "/api/messages")
        response = conn.getresponse()
        print(f"Status: {response.status} {response.reason}")
        data = response.read()
        print(f"Response: {data.decode()}")

        # Test 3: Send a test message
        print("\nTest 3: Testing POST /api/messages")
        headers = {'Content-type': 'application/json'}
        message = json.dumps({"content": "Test message"})
        conn.request("POST", "/api/messages", message, headers)
        response = conn.getresponse()
        print(f"Status: {response.status} {response.reason}")
        data = response.read()
        print(f"Response: {data.decode()}")

        print("\nAll tests completed successfully!")

    except Exception as e:
        print(f"Error during testing: {str(e)}")
    finally:
        conn.close()

def main():
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # This ensures the thread will be terminated when the main program exits
    
    print("Starting server...")
    server_thread.start()
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    print("Running tests...")
    test_server_response()
    
    print("\nTests finished. Press Ctrl+C to exit.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
