from backend.database import get_db_connection
from backend.services.employee_service import (
    get_employee_logic,
    get_all_employees_logic,
    update_employee_logic,
    filter_field_by_role,
    update_wellness_logic,
    get_employee_logic,
    submit_expense_logic,

)
from backend.services.document_service import search_hr_documents_logic, search_confidential_projects_logic


def submit_expense(expense_type: str, amount: float, description: str, user_role: str = None, employee_id: int = None):
    if employee_id is None:
        return {"error": "No employee_id in session - cannot retrieve info"}

    db = get_db_connection()

    try:
        result = submit_expense_logic(employee_id, amount, db)
        result["expense_type"] = expense_type
        result["description"] = description
        return result
    except ValueError as e:
        return {"error": str(e)}
    finally:
        db.close()


def get_my_info(user_role: str = None, employee_id: int = None):
    if employee_id is None:
        return {"error": "No employee_id in session — cannot retrieve info"}

    db = get_db_connection()

    try:
        employee = get_employee_logic(employee_id, db)
        return {
            "salary": employee.salary,
            "wellness": employee.wellness,
            "expense_amount": employee.expense_amount,
        }
    except ValueError as e:

        return {"error": str(e)}

    finally:
        db.close()


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


def search_hr_documents(query: str, user_role: str = None, employee_id: int = None):
    return search_hr_documents_logic(query)


def get_all_employees(user_role: str = None, employee_id: int = None):
    db = get_db_connection()
    try:
        employees = get_all_employees_logic(db)
        return [filter_field_by_role(emp, user_role) for emp in employees]
    finally:
        db.close()


CONFIDENTIAL_PROJECTS_PASSWORD = "access_code_2026"


def access_confidential_project(project_code: str, query: str, user_role: str = None, employee_id: int = None):
    if user_role != "HR":
        return {"error": "Access denied."}

    if project_code != CONFIDENTIAL_PROJECTS_PASSWORD:
        return {"error": "Invalid password !!"}

    return search_confidential_projects_logic(query)


AVAILABLE_FUNCTIONS = {
    "get_all_employees": get_all_employees,
    "search_hr_documents": search_hr_documents,
    "update_my_wellness": update_my_wellness,
    "get_my_info": get_my_info,
    "submit_expense": submit_expense,
    "access_confidential_project": access_confidential_project
}
