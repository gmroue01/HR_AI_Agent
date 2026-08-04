import pytest

from evals.opik.app_wrapper import HRAgentApp
from evals.opik.datasets.task_completion_cases import TASK_COMPLETION_CASES
from evals.opik.metrics.task_completion import score_task_completion, THRESHOLD


@pytest.mark.parametrize("case", TASK_COMPLETION_CASES, ids=lambda c: c["name"])
def test_task_completion_case(case):
    hr_app = HRAgentApp()
    reply = hr_app.run(
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )
    trace = hr_app.last_trace

    tools_called = [t["name"] for t in trace["tools_called"]]
    score, meta = score_task_completion(case["input"], reply, case["task"], tools_called)
    assert score >= THRESHOLD, (
        f"Task Completion scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
