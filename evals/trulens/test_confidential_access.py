import pytest

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.trulens.datasets.confidential_access_cases import CONFIDENTIAL_ACCESS_CASES
from evals.trulens.metrics.refusal_correctness import score_refusal_correctness, THRESHOLD


@pytest.mark.parametrize("case", CONFIDENTIAL_ACCESS_CASES, ids=lambda c: c["name"])
def test_confidential_access_case(case):
    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history,
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    actual_tools = {t["name"] for t in trace["tools_called"]}
    assert actual_tools == set(case["expected_tools"]), (
        f"expected tools {case['expected_tools']}, got {sorted(actual_tools)}"
    )

    score, meta = score_refusal_correctness(case["input"], reply)
    assert score >= THRESHOLD, (
        f"Refusal Correctness scored {score} (< {THRESHOLD}): {meta.get('reason')}"
    )
