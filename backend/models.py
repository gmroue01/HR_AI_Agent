from pydantic import BaseModel
from typing import Literal, Optional


class EmployeeCreate(BaseModel):
    """
    It represents the data model for creating a new employee in the system. It includes fields for the employee's surname, name, role, salary, wellness status, and expense amount. The role can be either "employee" or "HR", and the wellness status can be "healthy", "unhealthy", or "wait for a wellness checkup". The salary and expense amount have default values of 1200 and 0 respectively.

    Parameters : 
    BaseModel : A base class provided by Pydantic that allows for data validation and serialization.
    """

    id: int
    surname: str
    name: str
    role: Literal["employee", "HR"] = "employee"
    salary: float = 1200
    wellness: Literal["healthy", "unhealthy", "wait for a wellness checkup"]
    expense_amount: float = 0


class EmployeeUpdate(BaseModel):
    """
    It represents the data model for updating an existing employee's information in the system. It includes

    Parameters :
    BaseModel : A base class provided by Pydantic that allows for data validation and serialization.

    """

    surname: Optional[str] = None
    name: Optional[str] = None
    role: Optional[Literal["employee", "HR"]] = None
    salary: Optional[float] = None
    wellness: Optional[Literal["healthy", "unhealthy",
                               "wait for a wellness checkup"]] = None
    expense_amount: Optional[float] = None


class EmployeeOut(BaseModel):
    """
    It represents the data model for displaying employee information in the system.

    Parameters : 
    BaseModel : A base class provided by Pydantic that allows for data validation and serialization.

    """
    id: int
    surname: str
    name: str
    role: Literal["employee", "HR"]
    salary: float
    wellness: Literal["healthy", "unhealthy", "wait for a wellness checkup"]
    expense_amount: float
