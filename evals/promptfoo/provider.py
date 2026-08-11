import sys
from pathlib import Path

# promptfoo's Python wrapper only puts this file's own directory on sys.path;
# add the repo root so `chatbot_core` and `backend.*` (absolute imports) resolve.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.database import get_db_connection
from chatbot_core import SYSTEM_PROMPT, run_agent_turn

TEST_EMPLOYEE_ID = 1


def _reset_test_employee_expense():
    """Same reset as evals/shared/conftest.py's reset_test_employee_expense
    fixture, replicated here since promptfoo test cases aren't pytest fixtures —
    keeps results reproducible regardless of run order or prior manual testing."""
    db = get_db_connection()
    db.execute("UPDATE employees SET expense_amount = 0 WHERE id = 1")
    db.commit()
    db.close()


def call_api(prompt, options, context):
    vars_ = (context or {}).get("vars", {}) or {}
    user_role = vars_.get("user_role", "employee")

    _reset_test_employee_expense()

    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history, prompt,
        user_role=user_role, employee_id=TEST_EMPLOYEE_ID,
    )

    return {
        "output": reply,
        "metadata": {
            "tools_called": [
                {"name": t["name"], "arguments": t["arguments"]}
                for t in trace["tools_called"]
            ],
            "retrieved_chunks": [
                chunk["text"] for chunk in trace["retrieved_chunks"]
            ],
        },
    }
