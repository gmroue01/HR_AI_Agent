import pytest

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.trulens.datasets.task_completion_cases import TASK_COMPLETION_CASES
from evals.trulens.metrics.task_completion import score_task_completion, THRESHOLD


@pytest.mark.parametrize("case", TASK_COMPLETION_CASES, ids=lambda c: c["name"])
def test_task_completion_case(case):
    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history,
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    tools_called = [t["name"] for t in trace["tools_called"]]
    score, meta = score_task_completion(case["input"], reply, case["task"], tools_called)
    assert score >= THRESHOLD, (
        f"Task Completion scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
