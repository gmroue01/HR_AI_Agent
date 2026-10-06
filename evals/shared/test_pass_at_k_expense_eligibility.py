import math
import pytest

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.cases.expense_eligibility import EXPENSE_ELIGIBILITY_CASES

REPETITIONS = 10
K = 3
PASS_AT_K_THRESHOLD = 0.7


    
def pass_at_k(n: int, c: int, k: int) -> float:
    """
    Unbiased pass@k estimator from the Codex/HumanEval paper: probability
    that at least one of k independent samples is correct, estimated from n
    observed samples (c of them correct). Numerically stable product form,
    equivalent to 1 - C(n-c, k) / C(n, k) without computing raw (and
    potentially huge) binomial coefficients directly.
    """
    if n - c < k:
        return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


def _is_correct(user_role: str, message: str, expected_tools: set[str]) -> bool:
    chat_history = [SYSTEM_PROMPT]
    _, _, trace = run_agent_turn(
        chat_history, message, user_role=user_role, employee_id=1)
    tools_called = {call["name"] for call in trace["tools_called"]}
    return tools_called == expected_tools


@pytest.mark.parametrize("case", EXPENSE_ELIGIBILITY_CASES, ids=lambda c: c["name"])
def test_pass_at_k_meets_threshold(case):
    expected_tools = set(case["expected_tools"])

    # Same exact-match correctness proxy McNemar/metamorphic use for tool
    # calling — no LLM judge involved, so pass@k measures the agent's own
    # sampling reliability, not variance in a judge's opinion.
    correct_count = sum(
        _is_correct(case["user_role"], case["input"], expected_tools)
        for _ in range(REPETITIONS)
    )

    score = pass_at_k(REPETITIONS, correct_count, K)

    assert score >= PASS_AT_K_THRESHOLD, (
        f"pass@{K} for '{case['name']}' is {score:.3f} (< {PASS_AT_K_THRESHOLD}) — "
        f"only {correct_count}/{REPETITIONS} repetitions called the exact "
        f"expected tool set {sorted(expected_tools)}"
    )
