from fastapi import FastAPI, Depends, HTTPException
import sqlite3
from backend.database import get_db
from backend.models import EmployeeCreate, EmployeeUpdate, EmployeeOut

app = FastAPI()


FIELD_VISIBILIY = {
    "employee": {"id", "surname", "name", "role"},
    "HR": {"id", "surname", "name", "salary", "role", "wellness", "expense_amount"}
}


def filter_field_by_role(record: dict, user_role: str) -> dict:
    allowed_fields = FIELD_VISIBILIY.get(
        user_role, FIELD_VISIBILIY["employee"])
    return {k: v for k, v in record.items() if k in allowed_fields}


# Create a new employee
def create_employee_logic(employee: EmployeeCreate, db: sqlite3.Connection = Depends(get_db)):
    """
        Insert a new employee into the database and return the created employee.

        Args: 
            employee (EmployeeCreate): The employee data to be inserted.
            db (sqlite3.Connection): The database connection, provided by the get_db dependency.

        Returns:
            EmployeeOut: The newly created employee data.

        Raises :
            HTTPException: HTTPException: 409 if a database integrity constraint is violated
            (e.g. duplicate unique field).

    """

    try:
        cursor = db.execute(
            """INSERT INTO employees (surname, name, role, salary, wellness, expense_amount) VALUES (?, ?, ?, ?, ?, ?)""",
            (employee.surname, employee.name, employee.role,
             employee.salary, employee.wellness, employee.expense_amount)
        )
        db.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=409, detail=str(e))

    row = db.execute("SELECT * FROM employees WHERE id = ?",
                     (new_id,)).fetchone()
    return EmployeeOut(**row)


# Get all employees
def get_all_employees_logic(db: sqlite3.Connection = Depends(get_db)):
    """
    Retrieve all the employee of the table

    Args: 

    db (sqlite3.Connection) : the database connection, provided by the get_db dependency.

    Returns: 

     A list of employee records as dictionaries, one per row. 




    """

    rows = db.execute("SELECT * FROM employees").fetchall()

    return [dict(row) for row in rows]


# Get a-one employee by id
def get_employee_logic(employee_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Retrieve an employee by their ID.

    Args:
        employee_id (int): The ID of the employee to retrieve.
        db (sqlite3.Connection): The database connection, provided by the get_db dependency.

    Returns:
        EmployeeOut: The employee data if found.

    Raises:
        HTTPException: If the employee is not found.
    """

    row = db.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeOut(**row)


# Update an existing employee
def update_employee_logic(employee_id: int, employee: EmployeeUpdate, db: sqlite3.Connection = Depends(get_db)):
    """
    Update an existing employee data

    Args:
        employeed_id (int) : the ID of the employee to retrieve.
        employee (EmployeeUpdate) : the employee data to be updated.
        db (sqlite3.Connection) : the database connection, provided by the get_db dependency.

    Returns:
        EmployeeOut : the updated employee data.

    Raises : 
        HTTPException : 404 error if the employee is not found.

    """

    existing_employee = db.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    if existing_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    updates = employee.model_dump(exclude_unset=True)
    if not updates:
        return dict(existing_employee)

    # define the sql command
    set_clause = ",".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [employee_id]

    db.execute(f"UPDATE employees SET {set_clause} WHERE id = ?", values)
    db.commit()

    row = db.execute("SELECT * FROM employees WHERE id = ?",
                     (employee_id,)).fetchone()
    return EmployeeOut(**row)


def delete_employee_logic(employee_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Delete one employee by id.

    Args:

        employee_id (int) : the ID of the employee to delete.
        db (sqlite3.Connection) :  the database connection, provided by the get_db dependency.

    Returns: 

        get_all_employees(db) : function to print the entire and updated database.

    Raises:
        HTTPException : 404 error if employee is not found.

    """

    # use fetchone to return only the first row retrieve

    results = db.execute(f"DELETE FROM employees WHERE id = ?", (employee_id,))
    db.commit()

    if results.rowcount == 0:
        raise HTTPException(status_code=404, detail="Employee not found")


def update_wellness_logic(employee_id: int, wellness: str, db) -> dict:
    valid_values = {"healthy", "unhealthy", "wait for a wellness checkup"}
    if wellness not in valid_values:
        raise ValueError(f"Invalid wellness value : {wellness}")

    existing = db.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    if existing is None:
        raise ValueError("Employee not found")

    db.execute("UPDATE employees SET wellness = ? WHERE id = ?",
               (wellness, employee_id))
    db.commit()

    row = db.execute("SELECT * FROM employees WHERE id = ?",
                     (employee_id,)).fetchone()
    return dict(row)
