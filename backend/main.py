from fastapi import FastAPI, Depends, HTTPException
import sqlite3
from database import get_db
from models import EmployeeCreate, EmployeeUpdate, EmployeeOut


app = FastAPI()

# Create a new employee


@app.post("/employees/", response_model=EmployeeOut, status_code=201)
def create_employee(employee: EmployeeCreate, db: sqlite3.Connection = Depends(get_db)):
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
