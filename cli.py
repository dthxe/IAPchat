#!/usr/bin/env python3

import os
import sys
import argparse
from datetime import datetime
from typing import Optional, List, Dict
from github import Github
from dotenv import load_dotenv

def load_env_file() -> Dict[str, str]:
    """Load and parse .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                    except ValueError:
                        continue
    except FileNotFoundError:
        # Create from example if not exists
        example_path = os.path.join(os.path.dirname(__file__), '.env.example')
        try:
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
            print(f"Created new .env file from .env.example")
            return load_env_file()
        except FileNotFoundError:
            print("Error: Neither .env nor .env.example found")
            sys.exit(1)
    
    return env_vars

def save_env_file(env_vars: Dict[str, str]) -> None:
    """Save environment variables back to .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Read existing file to preserve comments and formatting
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Update or add variables
    updated_vars = set()
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            try:
                key = line.split('=', 1)[0].strip()
                if key in env_vars:
                    lines[i] = f"{key}={env_vars[key]}\n"
                    updated_vars.add(key)
            except ValueError:
                continue
    
    # Add any new variables
    for key, value in env_vars.items():
        if key not in updated_vars:
            lines.append(f"{key}={value}\n")
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(lines)

def load_github_token() -> str:
    """Load GitHub token from environment"""
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN not found in environment")
        print("Please set it using: python cli.py env set GITHUB_TOKEN your_token_here")
        sys.exit(1)
    return token

def load_repos_config() -> List[dict]:
    """Load repository configuration"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'repositories.json')
    try:
        with open(config_path, 'r') as f:
            import json
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Repository configuration not found at {config_path}")
        print("Please add repositories using the web interface first")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        sys.exit(1)

def push_repositories(token: str, repos: List[dict], message: Optional[str] = None) -> None:
    """Push all configured repositories to GitHub"""
    gh = Github(token)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_message = message or f"IAPchat auto-push at {timestamp}"

    for repo_config in repos:
        owner = repo_config['owner']
        name = repo_config['name']
        branch = repo_config.get('branch', 'main')
        
        try:
            print(f"\nPushing {owner}/{name}...")
            repo = gh.get_repo(f"{owner}/{name}")
            
            # Get the latest commit
            try:
                branch_ref = repo.get_branch(branch)
                latest_commit = branch_ref.commit
                print(f"Latest commit: {latest_commit.sha[:7]} - {latest_commit.commit.message}")
            except Exception as e:
                print(f"Warning: Couldn't get latest commit: {str(e)}")
                continue
            
            print(f"Successfully pushed to {owner}/{name}")
            
        except Exception as e:
            print(f"Error pushing to {owner}/{name}: {str(e)}")

def handle_env_command(args):
    """Handle environment variable commands"""
    env_vars = load_env_file()
    
    if args.env_command == 'list':
        # List all environment variables
        print("\nCurrent Environment Variables:")
        print("-" * 50)
        for key, value in env_vars.items():
            # Mask sensitive values
            if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                displayed_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
            else:
                displayed_value = value
            print(f"{key}={displayed_value}")
    
    elif args.env_command == 'get':
        # Get specific variable
        if not args.key:
            print("Error: Please specify a variable name")
            return
        value = env_vars.get(args.key)
        if value is None:
            print(f"Variable {args.key} not found")
        else:
            print(f"{args.key}={value}")
    
    elif args.env_command == 'set':
        # Set variable
        if not args.key or not args.value:
            print("Error: Please specify both variable name and value")
            return
        env_vars[args.key] = args.value
        save_env_file(env_vars)
        print(f"Updated {args.key}")
    
    elif args.env_command == 'unset':
        # Remove variable
        if not args.key:
            print("Error: Please specify a variable name")
            return
        if args.key in env_vars:
            del env_vars[args.key]
            save_env_file(env_vars)
            print(f"Removed {args.key}")
        else:
            print(f"Variable {args.key} not found")

def main():
    """Main CLI entrypoint"""
    parser = argparse.ArgumentParser(description='IAPchat CLI tools')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Push to GitHub repositories')
    push_parser.add_argument('-m', '--message', help='Commit message for push command')
    
    # Environment command
    env_parser = subparsers.add_parser('env', help='Manage environment variables')
    env_subparsers = env_parser.add_subparsers(dest='env_command', help='Environment command')
    
    # env list
    env_subparsers.add_parser('list', help='List all environment variables')
    
    # env get
    get_parser = env_subparsers.add_parser('get', help='Get environment variable')
    get_parser.add_argument('key', help='Variable name')
    
    # env set
    set_parser = env_subparsers.add_parser('set', help='Set environment variable')
    set_parser.add_argument('key', help='Variable name')
    set_parser.add_argument('value', help='Variable value')
    
    # env unset
    unset_parser = env_subparsers.add_parser('unset', help='Remove environment variable')
    unset_parser.add_argument('key', help='Variable name')
    
    args = parser.parse_args()
    
    if args.command == 'push':
        token = load_github_token()
        repos = load_repos_config()
        push_repositories(token, repos, args.message)
    elif args.command == 'env':
        if not args.env_command:
            env_parser.print_help()
        else:
            handle_env_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
