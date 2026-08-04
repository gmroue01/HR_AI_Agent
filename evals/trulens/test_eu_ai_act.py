import pytest

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.trulens.datasets.eu_ai_act_cases import EU_AI_ACT_CASES
from evals.trulens.metrics.eu_ai_act import score_eu_ai_act_compliance, THRESHOLD


@pytest.mark.parametrize("case", EU_AI_ACT_CASES, ids=lambda c: c["name"])
def test_eu_ai_act_case(case):
    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history,
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    score, meta = score_eu_ai_act_compliance(case["input"], reply)
    assert score >= THRESHOLD, (
        f"EU AI Act Compliance scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
