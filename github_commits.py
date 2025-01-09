#!/usr/bin/env python3

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

class GitHubCommitFetcher:
    """Class to fetch and parse commit messages from GitHub repositories"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the fetcher with GitHub authentication token
        
        Args:
            token: GitHub personal access token. If None, tries to load from environment
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token to constructor")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'

    def get_commits(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> List[Dict]:
        """
        Fetch commit messages from a repository
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            per_page: Number of commits per page (max 100)
            page: Page number to fetch
            
        Returns:
            List of dictionaries containing commit information:
            {
                'sha': commit hash,
                'message': commit message,
                'author': author name,
                'author_email': author email,
                'date': commit date,
                'url': commit URL
            }
        
        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If invalid parameters provided
        """
        if not owner or not repo:
            raise ValueError("Repository owner and name are required")
        
        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")
        
        url = f'{self.base_url}/repos/{owner}/{repo}/commits'
        params = {
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            commits = []
            for commit_data in response.json():
                commit = commit_data['commit']
                commits.append({
                    'sha': commit_data['sha'],
                    'message': commit['message'],
                    'author': commit['author']['name'],
                    'author_email': commit['author']['email'],
                    'date': commit['author']['date'],
                    'url': commit_data['html_url']
                })
            
            return commits
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commits: {str(e)}")
            if response.status_code == 404:
                print("Repository not found or private")
            elif response.status_code == 403:
                print("API rate limit exceeded or authentication required")
            raise

    def get_commit_by_sha(self, owner: str, repo: str, commit_sha: str) -> Dict:
        """
        Fetch a specific commit by its SHA
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            commit_sha: The SHA hash of the commit
            
        Returns:
            Dictionary containing commit information
            
        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If invalid parameters provided
        """
        if not owner or not repo or not commit_sha:
            raise ValueError("Repository owner, name and commit SHA are required")
            
        url = f'{self.base_url}/repos/{owner}/{repo}/commits/{commit_sha}'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            commit_data = response.json()
            commit = commit_data['commit']
            
            return {
                'sha': commit_data['sha'],
                'message': commit['message'],
                'author': commit['author']['name'],
                'author_email': commit['author']['email'],
                'date': commit['author']['date'],
                'url': commit_data['html_url']
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commit: {str(e)}")
            if response.status_code == 404:
                print("Commit or repository not found")
            elif response.status_code == 403:
                print("API rate limit exceeded or authentication required")
            raise

def main():
    """Example usage of the GitHubCommitFetcher"""
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Create fetcher instance
        fetcher = GitHubCommitFetcher()
        
        # Example: Fetch last 5 commits from a repository
        owner = "dth"  # Replace with repository owner
        repo = "IAPchat"   # Replace with repository name
        commits = fetcher.get_commits(owner, repo, per_page=5)
        
        print("\nLast 5 commits:")
        print("--------------")
        for commit in commits:
            print(f"SHA: {commit['sha'][:7]}")
            print(f"Author: {commit['author']} <{commit['author_email']}>")
            print(f"Date: {commit['date']}")
            print(f"Message: {commit['message']}")
            print(f"URL: {commit['url']}\n")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
