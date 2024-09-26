import sqlite3

def get_db_connection():
    return sqlite3.connect('watchlists.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS watchlists (
            user_id TEXT,
            symbol TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            user_id TEXT,
            symbol TEXT,
            target_price REAL,
            direction TEXT
        )
    ''')
    conn.commit()
    conn.close()
