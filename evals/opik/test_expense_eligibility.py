import pytest

from evals.opik.app_wrapper import HRAgentApp
from evals.opik.datasets.expense_eligibility_cases import EXPENSE_ELIGIBILITY_CASES
from evals.opik.metrics.eligibility_decision import (
    score_eligibility_decision,
    THRESHOLD as ELIGIBILITY_THRESHOLD,
)
from evals.opik.metrics.faithfulness import (
    score_faithfulness,
    THRESHOLD as FAITHFULNESS_THRESHOLD,
)


@pytest.mark.parametrize("case", EXPENSE_ELIGIBILITY_CASES, ids=lambda c: c["name"])
def test_expense_eligibility_case(case):
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

    retrieval_context = [chunk["text"] for chunk in trace["retrieved_chunks"]]
    assert retrieval_context, (
        f"No RAG context retrieved for case '{case['name']}' — "
        f"cannot evaluate faithfulness without retrieved chunks"
    )

    faith_score, faith_meta = score_faithfulness(case["input"], reply, retrieval_context)
    assert faith_score >= FAITHFULNESS_THRESHOLD, (
        f"Faithfulness scored {faith_score} (< {FAITHFULNESS_THRESHOLD}): {faith_meta.get('reason')}"
    )

    elig_score, elig_meta = score_eligibility_decision(case["input"], reply, retrieval_context)
    assert elig_score >= ELIGIBILITY_THRESHOLD, (
        f"Eligibility Decision Correctness scored {elig_score} "
        f"(< {ELIGIBILITY_THRESHOLD}): {elig_meta.get('reason')}"
    )
