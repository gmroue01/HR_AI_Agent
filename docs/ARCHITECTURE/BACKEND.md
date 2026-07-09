
This document explain all the aspect of the backend architecture and technical choice.

## Pydantic Usage: Type Hinting & Validation [`models.py`](./models.py)

Pydantic validates and type-checks incoming data before it reaches the application logic or the database.
This prevents malformed or incorrectly typed data from being inserted,
reducing runtime errors caused by invalid input.

The Pydantic logic is written in the [`models.py`](./models.py) script.

The script defines three classes:

- `EmployeeCreate(BaseModel)`: validates and type-checks the data required to insert a new employee into the database.
- `EmployeeUpdate(BaseModel)`: validates and type-checks partial updates to an existing employee's data. All fields are optional, allowing only the specified fields to be modified.
- `EmployeeOut(BaseModel)`: validates, type-checks, and filters the employee data returned by the API, ensuring only the intended fields are exposed to the client.

Note that these three class inherit from `BaseModel`, which provides the core validation and serialization logic. Check the Pydantic documentation for more details in (https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/).

**Design rationale:** separate classes per operation (rather than one model with optional 
fields) enforce stricter validation per context — e.g. `EmployeeOut` deliberately excludes 
sensitive fields (salary, SSN...) so the API response can never leak them even if the 
DB row contains them.




## Database connection [`database.py`](./database.py)

This script create the database connection.

The logic is simple.

The function `get_db()` is a generator function, allowing it to produce the connection value lazily, one at time, while preserving its execution state between calls.

It initializes the variable conn which is the output return from the function `sqlite3.connect()` which requires the database path file.

Next, it sets to the `row_factory` attribute to the SQlite `connection` object that controls how each row returned the query is represented in Python. Instead of tuples, query results are returned as `sqlite3.Row` objects, which support both index-based and name-based access to columns (e.g. `row[email]` instead of `row[3]`).

That enables straightforward conversion to a Python dictionnary via `dict(row)`, which is required to pass query results into Pydantic models.

The script takes in account that `SQLite3` does not enforce foreign key constraints by default.

`PRAGMA foreign keys = ON` must be executed on each connection to enable referential integrity checks.

```python
conn.execute("PRAGMA foreign_keys = ON")
```

It wrapps the `yield` in a `try/finaly` block ensures `conn.close()` runs even if the route raises an exception. Without this pattern, an error inside a route would leave the connection open indefinitly.


## API file ['main.py'](./main.py)

The FastApi application is callable by the `FastAPI()` function.

This file gathers all the API call function of the backend.

The avalaibles functions are the REST Endpoints:

    - `create_employee()` (POST): insert a new employee into the database and return the created employee
    - `get_all_employees(GET)` : retrieve all the employee of the table
    - `get_employee(GET)` : retrieve an employee by their ID.
    - `update_employee(PATH)` : Update an existing employee data.
    - `delete_employee(POST)`:  Delete one employee by ID.

Precisly, the decorators of all theses function implement the routing and the Python function implement the logic. 

In order to interact with the database, each function calls `Depends(get_db)`.

`Depends` is a special FastApi function that takes callable as `get_db()` function from `database.py` script.

### SQL Injection prevention :

Script uses the specific syntax in all SQL command in order to avoid SQL-injection.

```python
 "SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
```

Note that : 

- `?` is a placheholder.
- `(employee_id)` is argument replaced by the placeholder.
- `fetchone()` is a function that returns the first row.

So as to return all the rows, use `fetchall()`.

FastAPI provides a Swagger UI at  `http://127.0.0.1:8000/docs`, which lets us test routes directly in the browser.













