import pytest

from trulens.apps.app import TruApp
from evals.trulens.app_wrapper import HRAgentApp
from evals.trulens.feedback_functions import (
    f_context_relevance,
    f_groundedness,
    f_answer_relevance,
)
from evals.trulens.datasets.expense_eligibility_cases import EXPENSE_ELIGIBILITY_CASES
from evals.trulens.metrics.eligibility_decision import (
    score_eligibility_decision,
    THRESHOLD as ELIGIBILITY_THRESHOLD,
)

RAG_TRIAD_THRESHOLD = 0.8

hr_app = HRAgentApp()
tru_recorder = TruApp(
    hr_app,
    app_name="HR_agent",
    app_version="expense_eligibility",
    feedbacks=[f_context_relevance, f_groundedness, f_answer_relevance],
)


@pytest.mark.parametrize("case", EXPENSE_ELIGIBILITY_CASES, ids=lambda c: c["name"])
def test_expense_eligibility_case(case):
    with tru_recorder as recording:
        reply = hr_app.run(
            user_message=case["input"],
            user_role=case["user_role"],
            employee_id=1,
        )

    # hr_app.run() calls retrieve_context() internally, which stashes the
    # single agent call's trace on the instance — reused below instead of
    # calling the agent a second time.
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

    record = recording.get()
    scores = record.retrieve_feedback_results(timeout=60).iloc[0].to_dict()
    for name, score in scores.items():
        assert score is not None, (
            f"{name} did not return a score for case '{case['name']}' "
            f"(feedback computation failed or timed out)"
        )
        assert score >= RAG_TRIAD_THRESHOLD, (
            f"{name} scored {score} (< {RAG_TRIAD_THRESHOLD}) for case '{case['name']}'"
        )

    elig_score, elig_meta = score_eligibility_decision(
        case["input"], reply, retrieval_context)
    assert elig_score >= ELIGIBILITY_THRESHOLD, (
        f"Eligibility Decision Correctness scored {elig_score} "
        f"(< {ELIGIBILITY_THRESHOLD}): {elig_meta.get('reason')}"
    )
