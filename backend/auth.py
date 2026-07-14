from backend.database import get_db_connection


def login(surname: str, name: str) -> dict | None:
    db = get_db_connection()

    try:
        user = db.execute(
            "SELECT id, surname, name, role FROM employees WHERE surname = ? AND name = ?", (surname, name)).fetchone()
    finally:
        db.close()
    if user:
        return dict(user)
    else:
        return None
