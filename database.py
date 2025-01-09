#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class ChatDatabase:
    """Handle all database operations for the chat application"""
    
    def __init__(self, db_path: str = "database/chat.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self._ensure_db_directory()
        self.conn = None
        self._create_connection()
        self._create_tables()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _create_connection(self) -> None:
        """Create a database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Enable foreign key support
            self.conn.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise Exception(f"Error connecting to database: {str(e)}")

    def _create_tables(self) -> None:
        """Create necessary tables if they don't exist"""
        try:
            with self.conn:
                # Create repositories table
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS repositories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        owner TEXT NOT NULL,
                        name TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT (datetime('now')),
                        UNIQUE(owner, name)
                    )
                ''')

                # Create messages table with repository support
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT (datetime('now'))
                    )
                ''')

                # Create message_commits table for multiple repository support
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS message_commits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER NOT NULL,
                        repository_id INTEGER NOT NULL,
                        commit_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT (datetime('now')),
                        FOREIGN KEY (message_id) REFERENCES messages(id),
                        FOREIGN KEY (repository_id) REFERENCES repositories(id),
                        UNIQUE(message_id, repository_id)
                    )
                ''')

                # Create indices
                self.conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                    ON messages(timestamp)
                ''')
                self.conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_message_commits_message 
                    ON message_commits(message_id)
                ''')

        except sqlite3.Error as e:
            raise Exception(f"Error creating tables: {str(e)}")

    def add_repository(self, owner: str, name: str) -> int:
        """
        Add a new repository to track
        
        Args:
            owner: Repository owner/organization
            name: Repository name
            
        Returns:
            Repository ID
        """
        try:
            with self.conn:
                cursor = self.conn.execute('''
                    INSERT OR IGNORE INTO repositories (owner, name)
                    VALUES (?, ?)
                ''', (owner, name))
                
                if cursor.rowcount == 0:
                    # Repository already exists, get its ID
                    cursor = self.conn.execute('''
                        SELECT id FROM repositories
                        WHERE owner = ? AND name = ?
                    ''', (owner, name))
                    return cursor.fetchone()[0]
                
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error adding repository: {str(e)}")

    def add_message(self, content: str, timestamp: str) -> int:
        """
        Add a new message to the database
        
        Args:
            content: The message content
            timestamp: ISO format timestamp
            
        Returns:
            The ID of the newly inserted message
        """
        try:
            with self.conn:
                cursor = self.conn.execute('''
                    INSERT INTO messages (content, timestamp)
                    VALUES (?, ?)
                ''', (content, timestamp))
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error adding message: {str(e)}")

    def update_message_commits(self, message_id: int, commit_hashes: Dict[str, str]) -> None:
        """
        Update commit hashes for a message across multiple repositories
        
        Args:
            message_id: The message ID
            commit_hashes: Dictionary mapping "owner/name" to commit hash
        """
        try:
            with self.conn:
                for repo_path, commit_hash in commit_hashes.items():
                    owner, name = repo_path.split('/')
                    
                    # Get repository ID
                    cursor = self.conn.execute('''
                        SELECT id FROM repositories
                        WHERE owner = ? AND name = ?
                    ''', (owner, name))
                    row = cursor.fetchone()
                    
                    if row:
                        repository_id = row[0]
                        # Update or insert commit hash
                        self.conn.execute('''
                            INSERT OR REPLACE INTO message_commits 
                            (message_id, repository_id, commit_hash)
                            VALUES (?, ?, ?)
                        ''', (message_id, repository_id, commit_hash))
        except sqlite3.Error as e:
            raise Exception(f"Error updating commit hashes: {str(e)}")

    def get_messages(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Retrieve messages with their commit hashes from all repositories
        
        Args:
            limit: Maximum number of messages to retrieve
            offset: Number of messages to skip
            
        Returns:
            List of message dictionaries with repository information
        """
        try:
            cursor = self.conn.execute('''
                SELECT 
                    m.id,
                    m.content,
                    m.timestamp,
                    m.created_at,
                    r.owner,
                    r.name,
                    mc.commit_hash
                FROM messages m
                LEFT JOIN message_commits mc ON m.id = mc.message_id
                LEFT JOIN repositories r ON mc.repository_id = r.id
                ORDER BY m.timestamp DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            # Group commits by message
            messages = {}
            for row in cursor.fetchall():
                message_id = row[0]
                if message_id not in messages:
                    messages[message_id] = {
                        'id': message_id,
                        'content': row[1],
                        'timestamp': row[2],
                        'created_at': row[3],
                        'repositories': {}
                    }
                
                if row[4] and row[5]:  # If repository info exists
                    repo_path = f"{row[4]}/{row[5]}"
                    messages[message_id]['repositories'][repo_path] = row[6]
            
            return list(messages.values())
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving messages: {str(e)}")

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

def init_database(db_path: str = "database/chat.db"):
    """Initialize the database and create tables"""
    db = ChatDatabase(db_path)
    print("Database initialized successfully!")
    return db

if __name__ == "__main__":
    init_database()
