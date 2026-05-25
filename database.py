import sqlite3

DATABASE_URL = "./indie_games.db"

def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draft_indie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            bug_density REAL,
            fps REAL,
            wishlist INTEGER,
            remaining_budget REAL,
            score REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
