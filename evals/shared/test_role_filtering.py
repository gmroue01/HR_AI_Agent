import pytest
from tools.dispatcher import get_all_employees


RESTRICTED_FIELDS = {"salary", "wellness", "expense_amount"}


def test_employee_role_never_sees_restricted_fields():

    result = get_all_employees(user_role="employee")

    assert len(result) > 0, "Test requires at least one employee in the database"

    for emp in result:
        leaked_fields = RESTRICTED_FIELDS & emp.keys()  # set intersection
        assert not leaked_fields, (
            f"PII leak : employee role saw restricted fields {leaked_fields}"
            f"in record {emp}"
        )


def test_hr_role_sees_all_fields():

    result = get_all_employees(user_role="HR")

    assert len(result) > 0, "Test requires at least one employee in the database"

    for emp in result:
        missing_fields = RESTRICTED_FIELDS - emp.keys()
        assert not missing_fields, (
            f"HR role is missing expected fields {missing_fields} in record {emp}"
        )


def test_unknown_role_defaults_to_restricive():
    result = get_all_employees(
        user_role="some_invalid_role_that_does_not_exist")

    for emp in result:
        leaked_fields = RESTRICTED_FIELDS & emp.keys()
        assert not leaked_fields, (
            f"Security default failure : unknown role saw restricted fields"
            f"{leaked_fields} - should default to the most restrictive visibility"
        )
