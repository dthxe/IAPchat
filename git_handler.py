#!/usr/bin/env python3

import os
from datetime import datetime
from typing import Optional
from github import Github
from pathlib import Path
import json
from dotenv import load_dotenv

class GitHandler:
    """Handle all Git operations for the chat application"""
    
    def __init__(self, repo_name: str = "IAPchat"):
        """
        Initialize Git handler
        
        Args:
            repo_name: Name of the GitHub repository
        """
        # Load environment variables
        load_dotenv()
        
        # Get GitHub token from environment variable
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
            
        # Initialize GitHub client
        self.github = Github(self.github_token)
        self.repo_name = repo_name
        self.user = self.github.get_user()
        
        # Get repository
        try:
            self.repo = self.github.get_repo(f"{self.user.login}/{repo_name}")
            print(f"Connected to repository: {repo_name}")
        except Exception as e:
            print(f"Error connecting to repository: {str(e)}")
            raise

    def store_message(self, message_content: str, message_id: int) -> Optional[str]:
        """
        Store a message in the Git repository
        
        Args:
            message_content: Content of the message
            message_id: Database ID of the message
            
        Returns:
            The commit hash if successful, None otherwise
        """
        try:
            # Create message data
            message_data = {
                'content': message_content,
                'timestamp': datetime.now().isoformat(),
                'id': message_id
            }
            
            # Create file path based on timestamp
            timestamp = datetime.now().strftime('%Y/%m/%d/%H_%M_%S')
            file_path = f"chat_messages/{timestamp}_{message_id}.json"
            
            # Create message content
            content = json.dumps(message_data, indent=2)
            
            # Create or update file in repository
            try:
                # Try to get existing file
                file = self.repo.get_contents(file_path)
                self.repo.update_file(
                    file_path,
                    f"Update message {message_id}",
                    content,
                    file.sha
                )
            except Exception:
                # File doesn't exist, create it
                self.repo.create_file(
                    file_path,
                    f"Add message {message_id}",
                    content
                )
            
            # Get the latest commit
            commit = self.repo.get_commits()[0]
            return commit.sha
            
        except Exception as e:
            print(f"Error storing message: {str(e)}")
            return None

    def get_message(self, file_path: str) -> Optional[dict]:
        """
        Retrieve a message from the Git repository
        
        Args:
            file_path: Path to the message file
            
        Returns:
            Message data as dictionary if found, None otherwise
        """
        try:
            # Get file content
            file = self.repo.get_contents(file_path)
            content = file.decoded_content.decode('utf-8')
            
            # Parse JSON content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error retrieving message: {str(e)}")
            return None

def init_git_handler():
    """Initialize Git handler"""
    return GitHandler()

if __name__ == "__main__":
    # Test the Git handler
    try:
        handler = init_git_handler()
        
        # Test storing a message
        print("Testing message storage...")
        commit_hash = handler.store_message("Test message from git_handler.py", 1)
        if commit_hash:
            print(f"Message stored successfully. Commit hash: {commit_hash}")
        
        # Test retrieving the message
        print("\nTesting message retrieval...")
        # Get the latest file from the chat_messages directory
        try:
            contents = handler.repo.get_contents("chat_messages")
            if contents:
                latest_file = contents[-1]
                message = handler.get_message(latest_file.path)
                print(f"Retrieved message: {json.dumps(message, indent=2)}")
        except Exception as e:
            print(f"No messages found: {str(e)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
