import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv('DB_PATH', 'ito_game.db')

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS theme_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES theme_categories(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                host_name TEXT NOT NULL,
                status TEXT DEFAULT 'waiting',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                is_host INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(id),
                UNIQUE(room_id, name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                theme_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                status TEXT DEFAULT 'answering',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                duration_seconds INTEGER,
                FOREIGN KEY (room_id) REFERENCES rooms(id),
                FOREIGN KEY (theme_id) REFERENCES themes(id),
                FOREIGN KEY (category_id) REFERENCES theme_categories(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                secret_number INTEGER NOT NULL,
                answer TEXT,
                confirmed INTEGER DEFAULT 0,
                revealed INTEGER DEFAULT 0,
                reveal_order INTEGER,
                answered_at TIMESTAMP,
                FOREIGN KEY (round_id) REFERENCES rounds(id),
                FOREIGN KEY (player_id) REFERENCES players(id),
                UNIQUE(round_id, player_id)
            )
        ''')
        
        conn.commit()

if __name__ == '__main__':
    init_database()
    print(f"Database initialized at {DB_PATH}")
