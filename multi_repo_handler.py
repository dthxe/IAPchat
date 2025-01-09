#!/usr/bin/env python3

import os
from typing import List, Dict, Optional
from datetime import datetime
import json
from github import Github
from dotenv import load_dotenv
import asyncio
import aiohttp
from collections import defaultdict

class MultiRepoHandler:
    """Handle interactions with multiple GitHub repositories"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize with GitHub token and repositories configuration
        
        Args:
            token: GitHub personal access token. If None, tries to load from environment
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required")
        
        self.gh = Github(self.token)
        self.repos_config = self._load_repos_config()
        
    def _load_repos_config(self) -> List[Dict]:
        """Load repository configuration from config file"""
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'repositories.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config with current repository
            default_config = [{
                'owner': 'dth',
                'name': 'IAPchat',
                'branch': 'main',
                'message_path': 'messages'
            }]
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    async def _fetch_messages_from_repo(
        self,
        session: aiohttp.ClientSession,
        repo_config: Dict
    ) -> List[Dict]:
        """
        Fetch messages from a single repository asynchronously
        
        Args:
            session: aiohttp client session
            repo_config: Repository configuration dictionary
            
        Returns:
            List of messages from the repository
        """
        owner = repo_config['owner']
        name = repo_config['name']
        path = repo_config['message_path']
        
        url = f'https://api.github.com/repos/{owner}/{name}/contents/{path}'
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 404:
                    return []
                
                contents = await response.json()
                if not isinstance(contents, list):
                    return []
                
                messages = []
                for item in contents:
                    if item['type'] != 'file' or not item['name'].endswith('.json'):
                        continue
                        
                    async with session.get(item['download_url'], headers=headers) as msg_response:
                        if msg_response.status == 200:
                            message = await msg_response.json()
                            message['repository'] = f"{owner}/{name}"
                            messages.append(message)
                
                return messages
                
        except Exception as e:
            print(f"Error fetching from {owner}/{name}: {str(e)}")
            return []

    async def get_all_messages(self) -> List[Dict]:
        """
        Fetch messages from all configured repositories
        
        Returns:
            List of messages from all repositories, sorted by timestamp
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_messages_from_repo(session, repo)
                for repo in self.repos_config
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Merge and sort all messages
            all_messages = []
            for messages in results:
                all_messages.extend(messages)
            
            # Sort by timestamp
            all_messages.sort(key=lambda x: x['timestamp'])
            return all_messages

    def store_message(self, message_content: str, message_id: int) -> Dict[str, str]:
        """
        Store message in all configured repositories
        
        Args:
            message_content: Content of the message
            message_id: Database ID of the message
            
        Returns:
            Dictionary mapping repository names to commit hashes
        """
        commit_hashes = {}
        timestamp = datetime.now().isoformat()
        
        message_data = {
            'id': message_id,
            'content': message_content,
            'timestamp': timestamp
        }
        
        for repo_config in self.repos_config:
            try:
                repo = self.gh.get_repo(f"{repo_config['owner']}/{repo_config['name']}")
                
                # Create message file
                file_path = f"{repo_config['message_path']}/message_{message_id}.json"
                repo.create_file(
                    path=file_path,
                    message=f"Add message {message_id}",
                    content=json.dumps(message_data, indent=2),
                    branch=repo_config['branch']
                )
                
                # Get commit hash
                commit = repo.get_branch(repo_config['branch']).commit
                commit_hashes[f"{repo_config['owner']}/{repo_config['name']}"] = commit.sha
                
            except Exception as e:
                print(f"Error storing in {repo_config['owner']}/{repo_config['name']}: {str(e)}")
        
        return commit_hashes

    def add_repository(self, owner: str, name: str, branch: str = 'main', message_path: str = 'messages') -> None:
        """
        Add a new repository to the configuration
        
        Args:
            owner: Repository owner/organization
            name: Repository name
            branch: Branch to use (default: main)
            message_path: Path where messages are stored (default: messages)
        """
        new_repo = {
            'owner': owner,
            'name': name,
            'branch': branch,
            'message_path': message_path
        }
        
        # Check if repository exists and is accessible
        try:
            self.gh.get_repo(f"{owner}/{name}")
        except Exception as e:
            raise ValueError(f"Repository {owner}/{name} not found or not accessible: {str(e)}")
        
        # Add to config if not already present
        if new_repo not in self.repos_config:
            self.repos_config.append(new_repo)
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'repositories.json')
            with open(config_path, 'w') as f:
                json.dump(self.repos_config, f, indent=2)

    def remove_repository(self, owner: str, name: str) -> None:
        """
        Remove a repository from the configuration
        
        Args:
            owner: Repository owner/organization
            name: Repository name
        """
        self.repos_config = [
            repo for repo in self.repos_config
            if not (repo['owner'] == owner and repo['name'] == name)
        ]
        
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'repositories.json')
        with open(config_path, 'w') as f:
            json.dump(self.repos_config, f, indent=2)
