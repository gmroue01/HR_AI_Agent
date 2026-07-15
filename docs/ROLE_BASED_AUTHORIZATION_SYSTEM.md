# User role system

The roles defined in the database table are :

- `employee` : a person who works in the company. This person has a name, surname, salary, wellness status and an expense amount. 
- `HR` : HR manager is an employee that has more permissions than an employee.


## Capturing the role:

The [`auth.py`](../backend/auth.py) script implements the login logic. Essentially, the only purpose of the login feature is to return the user's role. The role is persistently stored in the session using the `st.session_state`.

Moreover, the `run_agent_turn()` function has an explicit user role parameter. 


## Restrictions in the tool calls: 

In every tool call, `AVAILABLE_FUNCTIONS` takes the user role parameter in account.

In the [`employee_service.py`](../backend/services/employee_service.py) script, a `FIELD_VISIBILITY` dictionary specifies the columns that must be return based on the user's role.
```python
FIELD_VISIBILITY = {
    "employee": {"id", "surname", "name"},
    "HR": {"id", "surname", "name", "role", "salary", "wellness", "expense_amount"},
}
``` 

The `filter_field_by_role()` function ensures the allows fields are returned for any SQL command executed by the agent.

## Restriction in the System Prompt :

The other way to prevent a data leakage is to indicate in the system prompt which information can be accessed by which role.