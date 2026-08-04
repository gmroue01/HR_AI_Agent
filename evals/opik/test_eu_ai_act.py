import pytest

from evals.opik.app_wrapper import HRAgentApp
from evals.opik.datasets.eu_ai_act_cases import EU_AI_ACT_CASES
from evals.opik.metrics.eu_ai_act import score_eu_ai_act_compliance, THRESHOLD


@pytest.mark.parametrize("case", EU_AI_ACT_CASES, ids=lambda c: c["name"])
def test_eu_ai_act_case(case):
    hr_app = HRAgentApp()
    reply = hr_app.run(
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    score, meta = score_eu_ai_act_compliance(case["input"], reply)
    assert score >= THRESHOLD, (
        f"EU AI Act Compliance scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
