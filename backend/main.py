from fastapi import FastAPI, Depends, HTTPException
import sqlite3
from database import get_db
from models import EmployeeCreate, EmployeeUpdate, EmployeeOut


app = FastAPI()

# Create a new employee


@app.post("/employees/", response_model=EmployeeOut, status_code=201)
def create_employee(employee: EmployeeCreate, db: sqlite3.Connection = Depends(get_db)):
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
@app.get("/employees/all", response_model=list[EmployeeOut])
def get_all_employees(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM employees").fetchall()

    return [dict(row) for row in rows]
# Get a-one employee by id


@app.get("/employees/id/{employee_id}", response_model=EmployeeOut)
def get_employees(employee_id: int, db: sqlite3.Connection = Depends(get_db)):
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
@app.patch("/employees/{employee_id}/update", response_model=EmployeeOut)
def update_employee(employee_id: int, employee: EmployeeUpdate, db: sqlite3.Connection = Depends(get_db)):
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


@app.delete("/employee/delete/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: sqlite3.Connection = Depends(get_db())):
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

    # use fetchone to return only the first row retrieved
    existing_employee = db.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()

    if existing_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.execute(f"DELETE FROM employees WHERE id = {employee_id}")

    return get_all_employees(db)
