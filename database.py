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
        self.conn = self._create_connection()
        self._create_tables()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _create_connection(self) -> sqlite3.Connection:
        """Create a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable foreign key support
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            raise Exception(f"Error connecting to database: {str(e)}")

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            with self.conn:
                # Create messages table
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        git_commit_hash TEXT,
                        created_at TEXT NOT NULL DEFAULT (datetime('now'))
                    )
                ''')

                # Create an index on timestamp for faster querying
                self.conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                    ON messages(timestamp)
                ''')

        except sqlite3.Error as e:
            raise Exception(f"Error creating tables: {str(e)}")

    def add_message(self, content: str, timestamp: str, git_commit_hash: Optional[str] = None) -> int:
        """
        Add a new message to the database
        
        Args:
            content: The message content
            timestamp: ISO format timestamp
            git_commit_hash: Optional Git commit hash reference
            
        Returns:
            The ID of the newly inserted message
        """
        try:
            with self.conn:
                cursor = self.conn.execute('''
                    INSERT INTO messages (content, timestamp, git_commit_hash)
                    VALUES (?, ?, ?)
                ''', (content, timestamp, git_commit_hash))
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error adding message: {str(e)}")

    def get_messages(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Retrieve messages from the database
        
        Args:
            limit: Maximum number of messages to retrieve
            offset: Number of messages to skip
            
        Returns:
            List of message dictionaries
        """
        try:
            cursor = self.conn.execute('''
                SELECT id, content, timestamp, git_commit_hash, created_at
                FROM messages
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            return [{
                'id': row[0],
                'content': row[1],
                'timestamp': row[2],
                'git_commit_hash': row[3],
                'created_at': row[4]
            } for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving messages: {str(e)}")

    def get_message_by_id(self, message_id: int) -> Optional[Dict]:
        """
        Retrieve a specific message by its ID
        
        Args:
            message_id: The ID of the message to retrieve
            
        Returns:
            Message dictionary or None if not found
        """
        try:
            cursor = self.conn.execute('''
                SELECT id, content, timestamp, git_commit_hash, created_at
                FROM messages
                WHERE id = ?
            ''', (message_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'content': row[1],
                    'timestamp': row[2],
                    'git_commit_hash': row[3],
                    'created_at': row[4]
                }
            return None
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving message: {str(e)}")

    def update_git_commit_hash(self, message_id: int, git_commit_hash: str):
        """
        Update the Git commit hash for a message
        
        Args:
            message_id: The ID of the message to update
            git_commit_hash: The Git commit hash to associate with the message
        """
        try:
            with self.conn:
                self.conn.execute('''
                    UPDATE messages
                    SET git_commit_hash = ?
                    WHERE id = ?
                ''', (git_commit_hash, message_id))
        except sqlite3.Error as e:
            raise Exception(f"Error updating git commit hash: {str(e)}")

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

def init_database():
    """Initialize the database and create tables"""
    db = ChatDatabase()
    print("Database initialized successfully!")
    return db

if __name__ == "__main__":
    init_database()
