from backend.database import get_db
from backend.models import EmployeeUpdate
from backend.services.employee_service import (
    get_employee_logic,
    get_all_employees_logic,
    update_employee_logic,
)


def get_all_employees(user_role: str = "employee"):
    # Exemple de check d'autorisation basique — à remplacer par ta vraie matrice
    if user_role not in ("manager", "hr_admin"):
        return {"error": "Accès refusé : rôle insuffisant pour lister tous les employés"}
    db = next(get_db())
    try:
        return get_all_employees_logic(db)
    finally:
        db.close()


AVAILABLE_FUNCTIONS = {

    "get_all_employees": get_all_employees,

}
