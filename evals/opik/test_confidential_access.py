import pytest

from evals.opik.app_wrapper import HRAgentApp
from evals.opik.datasets.confidential_access_cases import CONFIDENTIAL_ACCESS_CASES
from evals.opik.metrics.refusal_correctness import score_refusal_correctness, THRESHOLD


@pytest.mark.parametrize("case", CONFIDENTIAL_ACCESS_CASES, ids=lambda c: c["name"])
def test_confidential_access_case(case):
    hr_app = HRAgentApp()
    reply = hr_app.run(
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )
    trace = hr_app.last_trace

    actual_tools = {t["name"] for t in trace["tools_called"]}
    assert actual_tools == set(case["expected_tools"]), (
        f"expected tools {case['expected_tools']}, got {sorted(actual_tools)}"
    )

    score, meta = score_refusal_correctness(case["input"], reply)
    assert score >= THRESHOLD, (
        f"Refusal Correctness scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
