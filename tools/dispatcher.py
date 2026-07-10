from backend.database import get_db_connection

from backend.models import EmployeeUpdate
from backend.services.employee_service import (
    get_employee_logic,
    get_all_employees_logic,
    update_employee_logic,
)


def get_all_employees(user_role: str = None):
    db = get_db_connection()
    try:
        return get_all_employees_logic(db)
    finally:
        db.close()


AVAILABLE_FUNCTIONS = {
    "get_all_employees": get_all_employees,
}
