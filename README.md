# Git-Backed Web Messaging Application

A lightweight web-based messaging application that uses Git as a backend storage system. This application allows users to send and receive messages through a simple web interface while maintaining message history using Git commits.

## Features

- Simple web-based messaging interface
- Git-backed message storage
- SQLite database for user management
- Real-time message updates
- Message history with timestamps
- Basic user authentication

## Tech Stack

- Backend: Python (No frameworks)
- Database: SQLite
- Frontend: HTML, CSS, JavaScript (Vanilla)
- Version Control & Storage: Git (via GitHub API)
- Server: Python's built-in HTTP server

## Project Structure

```
IAPchat/
├── README.md
├── .gitignore
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── index.html
│   └── login.html
├── database/
│   └── chat.db
├── server.py
├── database.py
├── git_handler.py
└── requirements.txt
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd IAPchat
   ```

2. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Set up GitHub API token:
   - Create a GitHub Personal Access Token with `repo` scope
   - Set the token as an environment variable:
     ```bash
     export GITHUB_TOKEN=your_token_here
     ```

4. Initialize the database:
   ```bash
   python3 database.py
   ```

5. Run the server:
   ```bash
   python3 server.py
   ```

6. Access the application:
   Open your web browser and navigate to `http://localhost:8000`

## Development Status

Project started: January 7, 2025
Status: In Development

## Security Notes

- Store GitHub tokens securely
- Never commit sensitive information
- Use environment variables for configuration
- Implement proper input validation

## License

MIT License - See LICENSE file for details
