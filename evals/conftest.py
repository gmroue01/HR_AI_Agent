from deepeval.test_case import ToolCall
from backend.database import get_db_connection
import pytest


def trace_to_tool_calls(trace: dict) -> list[ToolCall]:
    """"
    Transform the trace dict into a list of TooCall deepeval object

    Args:
        trace (dict) : the agent trace
    return: 
        list[ToolCall] : the list with all the corresponding ToolCall object.
    Raises:
        None

    """
    return [
        ToolCall(name=t["name"], input_parameters=t["arguments"])
        for t in trace["tools_called"]
    ]


@pytest.fixture(autouse=True)
def reset_test_employee_expense():
    """Remet expense_amount à 0 pour l'employé de test avant chaque test,
    pour garantir des résultats reproductibles indépendamment de l'ordre d'exécution
    ou des tests manuels précédents effectués via Streamlit."""
    db = get_db_connection()
    db.execute("UPDATE employees SET expense_amount = 0 WHERE id = 1")
    db.commit()
    db.close()
    yield
