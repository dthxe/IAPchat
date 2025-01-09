# Chat Application with GitHub Integration - Recreation Specification

## Overview
A chat application that integrates with GitHub to fetch and display commit messages, featuring a server-based architecture with SQLite storage and comprehensive test coverage.

## Core Components

### 1. Server Component
- **HTTP Server**: Custom implementation using Python's `http.server`
- **Request Handler**: Extended `SimpleHTTPRequestHandler` with custom routing
- **Database Integration**: SQLite-based message storage
- **GitHub Integration**: Commit message fetching capability

### 2. Database Structure
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repositories (
    id INTEGER PRIMARY KEY,
    owner TEXT NOT NULL,
    name TEXT NOT NULL,
    branch TEXT DEFAULT 'main',
    message_path TEXT DEFAULT 'messages'
);
```

### 3. API Endpoints

#### Messages
- `GET /api/messages`
  - Returns all chat messages
  - Response: JSON array of message objects
  ```json
  [
    {
      "id": 1,
      "content": "message text",
      "timestamp": "2025-01-08T18:41:59"
    }
  ]
  ```

- `POST /api/messages`
  - Adds a new message
  - Request body:
  ```json
  {
    "content": "message text"
  }
  ```
  - Response: 201 Created with message details

#### Repositories
- `POST /api/repositories`
  - Adds a new GitHub repository to monitor
  - Request body:
  ```json
  {
    "owner": "username",
    "name": "repo-name",
    "branch": "main",
    "message_path": "messages"
  }
  ```
  - Response: 201 Created with repository details

### 4. GitHub Integration
- GitHub personal access token required for authentication
- Capability to fetch commit messages from specified repositories
- Rate limit handling and error management
- Support for pagination of commit history

### 5. Static File Serving
- Serves static files from `/static` directory
- Handles HTML templates from `/templates` directory
- Default routes:
  - `/`: Main chat interface
  - `/login`: Login page
  - `/static/*`: Static assets

## Required Files

### 1. Core Application Files
- `server.py`: Main HTTP server implementation
- `database.py`: Database operations and management
- `github_commits.py`: GitHub API integration
- `multi_repo_handler.py`: Repository management

### 2. Test Files
- `test_endpoints.py`: API endpoint testing
- Test database configuration and cleanup

### 3. Configuration Files
- `.env`: Environment configuration
  ```
  GITHUB_TOKEN=your_github_token_here
  ```
- `.gitignore`: Standard Python gitignore file

## Dependencies
```
python>=3.6
requests
python-dotenv
sqlite3
```

## Testing Requirements
- Unit tests for all API endpoints
- Database operation tests
- GitHub integration tests
- Test database isolation
- Proper cleanup after tests

## Security Considerations
- GitHub token must be stored securely in `.env`
- No sensitive data in response payloads
- Input validation for all API endpoints
- Error handling for all external service calls

## Development Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Create `.env` file with GitHub token
5. Initialize database
6. Run tests to verify setup

## Running the Application
1. Set up environment variables
2. Initialize database
3. Start server:
   ```bash
   python server.py
   ```
4. Server will run on port 8000 by default

## Testing Instructions
Run tests with:
```bash
python -m unittest test_endpoints.py
```

This specification captures the core functionality of your existing chat application. To recreate the project, provide this specification and I will help you implement each component step by step, maintaining the same functionality and structure as your current implementation.
