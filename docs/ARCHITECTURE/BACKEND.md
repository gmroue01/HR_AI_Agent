
This document explain all the aspect of the backend architecture and technical choice.

## Pydantic Usage: Type Hinting & Validation

Pydantic validates and type-checks incoming data before it reaches the application logic or the database.
This prevents malformed or incorrectly typed data from being inserted,
reducing runtime errors caused by invalid input.

The Pydantic logic is written in the [`models.py`](./models.py) script.

The script defines three classes:

- `EmployeeCreate(BaseModel)`: validates and type-checks the data required to insert a new employee into the database.
- `EmployeeUpdate(BaseModel)`: validates and type-checks partial updates to an existing employee's data. All fields are optional, allowing only the specified fields to be modified.
- `EmployeeOut(BaseModel)`: validates, type-checks, and filters the employee data returned by the API, ensuring only the intended fields are exposed to the client.

Note that these three class inherit from `BaseModel`, which provides the core validation and serialization logic. Check the Pydantic documentation for more details in (https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/).

