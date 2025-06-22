import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

class DatabaseHandler:
    def __init__(self, db_path: str = "cache_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table to track different runs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    topic TEXT,
                    app_name TEXT,
                    app_description TEXT
                )
            ''')
            
            # Search agent results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    url TEXT,
                    snippet TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_response TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Twitter agent results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS twitter_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    url TEXT,
                    snippet TEXT,
                    screen_name TEXT,
                    followers_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    favorite_count INTEGER DEFAULT 0,
                    quote_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    retweet_count INTEGER DEFAULT 0,
                    raw_response TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Reviewer agent outputs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviewer_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    distilled_topics TEXT, -- JSON array of topics
                    talking_points TEXT,   -- JSON array of talking points
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_response TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Editor agent outputs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS editor_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    topic TEXT,
                    linkedin_post TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_response TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def create_session(self, session_name: str, topic: Optional[str] = None, app_name: Optional[str] = None, app_description: Optional[str] = None) -> int:
        """Create a new session and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (session_name, topic, app_name, app_description)
                VALUES (?, ?, ?, ?)
            ''', (session_name, topic, app_name, app_description))
            conn.commit()
            return cursor.lastrowid
    
    def get_sessions(self) -> List[Dict]:
        """Get all sessions ordered by creation date."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, session_name, created_at, topic, app_name, app_description
                FROM sessions 
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_latest_session_id(self) -> Optional[int]:
        """Get the ID of the most recent session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1')
            result = cursor.fetchone()
            return result[0] if result else None
    
    # Search Agent Methods
    def save_search_results(self, session_id: int, results: List[Dict], raw_response: Optional[str] = None):
        """Save search agent results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for result in results:
                cursor.execute('''
                    INSERT INTO search_results (session_id, url, snippet, raw_response)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, result.get('url'), result.get('snippet'), raw_response))
            conn.commit()
    
    def get_search_results(self, session_id: int = None) -> List[Dict]:
        """Get search results for a session (or latest if no session_id provided)."""
        if session_id is None:
            session_id = self.get_latest_session_id()
        
        if session_id is None:
            return []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url, snippet, created_at, raw_response
                FROM search_results 
                WHERE session_id = ?
                ORDER BY created_at
            ''', (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def has_search_results(self, session_id: int = None) -> bool:
        """Check if search results exist for a session."""
        if session_id is None:
            session_id = self.get_latest_session_id()
            
        if session_id is None:
            return False
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM search_results WHERE session_id = ?', (session_id,))
            return cursor.fetchone()[0] > 0
    
    # Twitter Agent Methods  
    def save_twitter_results(self, session_id: int, results: List[Dict], raw_response: Optional[str] = None):
        """Save twitter agent results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for result in results:
                cursor.execute('''
                    INSERT INTO twitter_results 
                    (session_id, url, snippet, screen_name, followers_count, 
                     favorite_count, quote_count, reply_count, retweet_count, raw_response)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, result.get('url'), result.get('snippet'), 
                      result.get('screen_name'), result.get('followers_count', 0),
                      result.get('favorite_count', 0), result.get('quote_count', 0),
                      result.get('reply_count', 0), result.get('retweet_count', 0), raw_response))
            conn.commit()
    
    def get_twitter_results(self, session_id: int = None) -> List[Dict]:
        """Get twitter results for a session (or latest if no session_id provided)."""
        if session_id is None:
            session_id = self.get_latest_session_id()
        
        if session_id is None:
            return []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url, snippet, screen_name, followers_count, created_at,
                       favorite_count, quote_count, reply_count, retweet_count, raw_response
                FROM twitter_results 
                WHERE session_id = ?
                ORDER BY created_at
            ''', (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def has_twitter_results(self, session_id: int = None) -> bool:
        """Check if twitter results exist for a session."""
        if session_id is None:
            session_id = self.get_latest_session_id()
            
        if session_id is None:
            return False
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM twitter_results WHERE session_id = ?', (session_id,))
            return cursor.fetchone()[0] > 0
    
    # Reviewer Agent Methods
    def save_reviewer_output(self, session_id: int, distilled_topics: List[str], talking_points: List[str], raw_response: Optional[str] = None):
        """Save reviewer agent output."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reviewer_outputs (session_id, distilled_topics, talking_points, raw_response)
                VALUES (?, ?, ?, ?)
            ''', (session_id, json.dumps(distilled_topics), json.dumps(talking_points), raw_response))
            conn.commit()
    
    def get_reviewer_output(self, session_id: int = None) -> Dict:
        """Get reviewer output for a session (or latest if no session_id provided)."""
        if session_id is None:
            session_id = self.get_latest_session_id()
        
        if session_id is None:
            return {"distilled_topics": [], "talking_points": []}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT distilled_topics, talking_points, created_at, raw_response
                FROM reviewer_outputs 
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (session_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "distilled_topics": json.loads(result['distilled_topics']),
                    "talking_points": json.loads(result['talking_points']),
                    "created_at": result['created_at'],
                    "raw_response": result['raw_response']
                }
            return {"distilled_topics": [], "talking_points": []}
    
    def has_reviewer_output(self, session_id: int = None) -> bool:
        """Check if reviewer output exists for a session."""
        if session_id is None:
            session_id = self.get_latest_session_id()
            
        if session_id is None:
            return False
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM reviewer_outputs WHERE session_id = ?', (session_id,))
            return cursor.fetchone()[0] > 0
    
    # Editor Agent Methods
    def save_editor_outputs(self, session_id: int, posts: List[Dict], raw_responses: Optional[List[str]] = None):
        """Save editor agent outputs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for i, post in enumerate(posts):
                raw_response = raw_responses[i] if raw_responses and i < len(raw_responses) else None
                cursor.execute('''
                    INSERT INTO editor_outputs (session_id, topic, linkedin_post, raw_response)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, post.get('topic'), post.get('linkedin_post'), raw_response))
            conn.commit()
    
    def get_editor_outputs(self, session_id: int = None) -> List[Dict]:
        """Get editor outputs for a session (or latest if no session_id provided)."""
        if session_id is None:
            session_id = self.get_latest_session_id()
        
        if session_id is None:
            return []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT topic, linkedin_post, created_at, raw_response
                FROM editor_outputs 
                WHERE session_id = ?
                ORDER BY created_at
            ''', (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def has_editor_outputs(self, session_id: int = None) -> bool:
        """Check if editor outputs exist for a session."""
        if session_id is None:
            session_id = self.get_latest_session_id()
            
        if session_id is None:
            return False
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM editor_outputs WHERE session_id = ?', (session_id,))
            return cursor.fetchone()[0] > 0