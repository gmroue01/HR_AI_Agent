from fastapi import APIRouter, Depends
import sqlite3

from backend.database import get_db
from backend.models import EmployeeCreate, EmployeeOut, EmployeeUpdate
from backend.services.employee_service import (
    create_employee_logic, update_employee_logic, get_all_employees_logic, get_employee_logic, delete_employee_logic,)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/", response=EmployeeOut, status_code=201)
def create_employee(employee: EmployeeCreate, db: sqlite3.Connection = Depends(get_db)):
    return create_employee_logic(employee, db)


@router.get("/id/{employee_id}", response=EmployeeOut, status_code=201)
def get_employee(employee_id: int, db: sqlite3.Connection = Depends(get_db)):
    return get_employee_logic(employee_id, db)


@router.get("/all", response=list[EmployeeOut])
def get_all_employee(employee_id: int, db: sqlite3.Connection = Depends(get_db)):
    return get_all_employees_logic(employee_id, db)


@router.patch("/{employee_id}/update", response=EmployeeOut)
def update_employee(employee_id: int, employee: EmployeeUpdate, db: sqlite3.Connection = Depends(get_db)):
    return update_employee_logic(employee_id, employee, db)


@router.delete("/{employee_id}/delete", status_code=204)
def delete_employee(employee_id: int, db: sqlite3.Connection = Depends(get_db)):
    delete_employee_logic(employee_id, db)
