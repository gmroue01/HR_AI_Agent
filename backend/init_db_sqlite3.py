import sqlite3


def init_db(db_path="app.db"):
    """
    Initilizes the SQLite database by creating the necessary tables if they do not already exist.
    """

    conn = sqlite3.connect(db_path)
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
