This documents gather all the test function documentation.


## [`test_role_filtering.py`](../evals test_role_filtering.py)

This script implements test about role filtering : Make sure the application does not give the permission to access to some private or sensitive data.

**private data** refers to employee's data that cannot be accessed by other employee except `HR` role.

The `set` **RESTRICTED_FIELDS** defines the three private data columns of any employee : `salary`, `wellness` and `expense_amount`.

- **`test_employee_role_never_sees_restricted_fields()`** 
- **`test_hr_role_sees_all_field()`**
- **`test_unknown_role_defaults_to_restrictive()`**


**What's not covered** :







