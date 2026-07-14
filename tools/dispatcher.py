from backend.database import get_db_connection

from backend.models import EmployeeUpdate
from backend.services.employee_service import (
    get_employee_logic,
    get_all_employees_logic,
    update_employee_logic,
    filter_field_by_role,
    update_wellness_logic
)
from backend.services.document_service import search_hr_documents_logic


def update_my_wellness(wellness: str, user_role: str = None, employee_id: int = None):
    if employee_id is None:
        return {"error": "No employee_id in session — cannot update wellness"}
    db = get_db_connection()

    try:
        return update_wellness_logic(employee_id, wellness, db)
    except ValueError as e:
        return {"error": str(e)}
    finally:
        db.close()


def search_hr_documents(query: str, user_role: str = None):
    return search_hr_documents_logic(query)


def get_all_employees(user_role: str = None):
    db = get_db_connection()
    try:
        employees = get_all_employees_logic(db)
        return [filter_field_by_role(emp, user_role) for emp in employees]
    finally:
        db.close()


AVAILABLE_FUNCTIONS = {
    "get_all_employees": get_all_employees,
    "search_hr_documents": search_hr_documents,
    "update_my_wellness": update_my_wellness
}
