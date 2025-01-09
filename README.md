# Git-Backed Chat Application

A real-time chat application that stores messages in both SQLite and GitHub repositories.

## Features

- Real-time messaging with web interface
- Message persistence in SQLite database
- Git-backed message storage across multiple repositories
- Async message fetching from multiple sources
- Clean and modern web interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A GitHub account with a Personal Access Token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dth/IAPchat.git
cd IAPchat
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# List current environment variables
python cli.py env list

# Set your GitHub token
python cli.py env set GITHUB_TOKEN your_token_here

# Get a specific variable
python cli.py env get GITHUB_TOKEN

# Remove a variable
python cli.py env unset VARIABLE_NAME
```

The CLI will:
- Create `.env` from `.env.example` if it doesn't exist
- Preserve comments and formatting when updating variables
- Mask sensitive values when displaying them
- Validate required variables

### GitHub Token Setup

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Give it a descriptive name (e.g., "IAPchat App")
4. Select the required scopes:
   - `repo` (Full control of private repositories)
   - `user` (Read-only access to user information)
5. Copy the generated token
6. Paste it in your `.env` file:
```env
GITHUB_TOKEN=your_token_here
```

## Running the Application

1. Start the server:
```bash
python server.py
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

## Managing Repositories

### Adding a Repository

Use the API endpoint to add a new repository:

```bash
curl -X POST http://localhost:8000/api/repositories \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "username",
    "name": "repo-name",
    "branch": "main",
    "message_path": "messages"
  }'
```

Or use the web interface at `http://localhost:8000/repositories`

### Pushing to Repositories

Use the CLI to push all repositories:

```bash
# Push with default commit message
python cli.py push

# Push with custom commit message
python cli.py push -m "Your commit message here"
```

The push command will:
1. Load your GitHub token from `.env`
2. Read repository configuration
3. Push all configured repositories to GitHub
4. Show status for each repository

### Repository Configuration

Each repository in the system requires:
- Owner (GitHub username or organization)
- Repository name
- Branch (defaults to 'main')
- Message path (defaults to 'messages')

## Development

### Running Tests

```bash
python test_endpoints.py
```

### Project Structure

- `server.py`: Main HTTP server and request handling
- `database.py`: SQLite database operations
- `multi_repo_handler.py`: GitHub repository management
- `templates/`: HTML templates
- `static/`: Static assets (CSS, JS)
- `config/`: Configuration files
- `database/`: SQLite database files

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **GitHub Token Issues**
   - Ensure your token has the required scopes
   - Check that the token is correctly set in `.env`
   - Verify the token is still valid in GitHub settings

2. **Database Issues**
   - Check write permissions in the database directory
   - Ensure SQLite is installed and working
   - Try deleting and recreating the database file

3. **Repository Access**
   - Verify repository exists and is accessible
   - Check repository permissions
   - Ensure branch name matches configuration

For more help, please open an issue on GitHub.
