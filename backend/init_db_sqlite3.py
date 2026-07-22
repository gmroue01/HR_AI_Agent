import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def init_db(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            surname TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee' CHECK (role IN ('employee', 'HR')),
            salary REAL NOT NULL DEFAULT 1200,
            wellness TEXT NOT NULL CHECK (wellness IN ('healthy', 'unhealthy', 'wait for a wellness checkup')),
            expense_amount REAL NOT NULL DEFAULT 0,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
