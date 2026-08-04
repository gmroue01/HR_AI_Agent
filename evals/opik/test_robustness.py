import pytest

from evals.opik.app_wrapper import HRAgentApp
from evals.opik.datasets.robustness_cases import ROBUSTNESS_CASES
from evals.opik.metrics.robustness import score_robustness, THRESHOLD


@pytest.mark.parametrize("case", ROBUSTNESS_CASES, ids=lambda c: c["name"])
def test_robustness_case(case):
    hr_app = HRAgentApp()
    reply = hr_app.run(
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    score, meta = score_robustness(case["input"], reply)
    assert score >= THRESHOLD, (
        f"Robustness scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
