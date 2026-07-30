import pytest

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.trulens.datasets.robustness_cases import ROBUSTNESS_CASES
from evals.trulens.metrics.robustness import score_robustness, THRESHOLD


@pytest.mark.parametrize("case", ROBUSTNESS_CASES, ids=lambda c: c["name"])
def test_robustness_case(case):
    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history,
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    score, meta = score_robustness(case["input"], reply)
    assert score >= THRESHOLD, (
        f"Robustness scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
