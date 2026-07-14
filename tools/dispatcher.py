from backend.database import get_db_connection

from backend.models import EmployeeUpdate
from backend.services.employee_service import (
    get_employee_logic,
    get_all_employees_logic,
    update_employee_logic,
)
from backend.services.document_service import search_hr_documents_logic


def search_hr_documents(query: str, user_role: str = None):
    return search_hr_documents_logic(query)


def get_all_employees(user_role: str = None):
    db = get_db_connection()
    try:
        return get_all_employees_logic(db)
    finally:
        db.close()


AVAILABLE_FUNCTIONS = {
    "get_all_employees": get_all_employees,
    "search_hr_documents": search_hr_documents
}
