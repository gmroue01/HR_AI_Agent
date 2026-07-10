import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def get_db():
    """
    Get a database connection.
    Make sur that the foreign key constraints are enforced by setting the PRAGMA foreign_keys to ON.
    Make sure that the connection is closed after use to avoid database locks.
    It returns a generator that yields a database connection object. The connection is closed after the generator is exhausted.

    Parameters : 

    No parameters are required for this function.

    Yields :
    sqlite3.Connection : A connection object to the SQLite database.

    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def get_db_connection() -> sqlite3.Connection:
    """Connexion directe, pour usage hors FastAPI (ex: dispatcher du chatbot)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
