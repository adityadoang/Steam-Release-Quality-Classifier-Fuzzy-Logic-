import sqlite3

DATABASE_URL = "./indie_games.db"

def init_db(reset=False):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    if reset:
        cursor.execute('DROP TABLE IF EXISTS draft_indie')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draft_indie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            bug_density REAL,
            fps REAL,
            wishlist INTEGER,
            remaining_budget REAL,
            score REAL,
            status TEXT,
            -- Fuzzy membership degrees
            mu_bug_sangat_bersih REAL,
            mu_bug_wajar REAL,
            mu_bug_rusak REAL,
            mu_fps_patah_patah REAL,
            mu_fps_stabil REAL,
            mu_fps_lancar REAL,
            mu_wishlist_sedikit REAL,
            mu_wishlist_menjanjikan REAL,
            mu_wishlist_meledak REAL,
            mu_budget_kritis REAL,
            mu_budget_aman REAL,
            mu_budget_melimpah REAL,
            mu_quality_tunda REAL,
            mu_quality_akses_awal REAL,
            mu_quality_siap_rilis REAL
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
