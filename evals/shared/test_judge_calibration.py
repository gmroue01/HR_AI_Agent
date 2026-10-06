import pytest
from deepeval.test_case import LLMTestCase

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.cases.expense_eligibility import EXPENSE_ELIGIBILITY_CASES
from evals.shared.cases.judge_calibration_labels import JUDGE_CALIBRATION_LABELS
from evals.deepeval.metrics.eligibility_decision import eligibility_decision_correctness

# Max |human_score - judge_score| still considered agreement. Not derived
# from any formal analysis — a starting point to revisit once real labels
# and a few calibration runs give an actual sense of the judge's noise floor.
AGREEMENT_TOLERANCE = 0.2


@pytest.mark.parametrize("case", EXPENSE_ELIGIBILITY_CASES, ids=lambda c: c["name"])
def test_judge_score_agrees_with_human_label(case):
    label = JUDGE_CALIBRATION_LABELS.get(case["name"], {})
    human_score = label.get("human_score")
    if human_score is None:
        pytest.skip(
            f"No human label recorded for '{case['name']}' — fill in "
            f"evals/shared/cases/judge_calibration_labels.py to enable this check"
        )

    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history, case["input"], user_role=case["user_role"], employee_id=1)
    retrieval_context = [chunk["text"] for chunk in trace["retrieved_chunks"]]

    if not retrieval_context:
        # Same non-deterministic gap test_permutation_expense_eligibility.py
        # hit: the agent occasionally skips search_hr_documents entirely, and
        # without retrieved policy text the judge has no ground truth to
        # score against either — not a calibration signal either way.
        pytest.skip(
            f"No RAG context retrieved for '{case['name']}' on this run — "
            f"cannot compare judge and human scores without it"
        )

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=reply,
        retrieval_context=retrieval_context,
    )
    judge_score = eligibility_decision_correctness.measure(
        test_case, _show_indicator=False)
    judge_reason = eligibility_decision_correctness.reason

    diff = abs(human_score - judge_score)
    assert diff <= AGREEMENT_TOLERANCE, (
        f"Judge/human disagreement on '{case['name']}': human={human_score} "
        f"({label.get('human_reason')}), judge={judge_score:.3f} ({judge_reason}) "
        f"— diff={diff:.3f} > tolerance {AGREEMENT_TOLERANCE}"
    )


# "Substantial agreement" on the Landis & Koch scale — a starting point, not
# derived from any formal analysis, same caveat as AGREEMENT_TOLERANCE above.
KAPPA_THRESHOLD = 0.6
KAPPA_MIN_LABELS = 2


def cohen_kappa(pairs: list[tuple[bool, bool]]) -> float | None:
    """
    Cohen's kappa for agreement between two raters on a binary classification,
    computed directly rather than pulling in scikit-learn/statsmodels for a
    formula this short:

        kappa = (p_o - p_e) / (1 - p_e)

    p_o is the observed agreement rate. p_e is the agreement expected by
    chance alone, derived from each rater's own marginal "pass" rate — the
    same role scipy.stats.binomtest's null hypothesis plays for McNemar's
    test elsewhere in this project, just for two raters instead of two
    conditions.

    Returns None if p_e == 1 (both raters would agree 100% of the time by
    chance alone, e.g. every pair is "pass" for both) — kappa is undefined
    there, the same reasoning McNemar's test uses to skip on zero discordant
    pairs rather than compute a meaningless ratio.
    """
    n = len(pairs)
    p_o = sum(h == j for h, j in pairs) / n

    human_pass_rate = sum(h for h, _ in pairs) / n
    judge_pass_rate = sum(j for _, j in pairs) / n
    p_e = (human_pass_rate * judge_pass_rate) + \
        ((1 - human_pass_rate) * (1 - judge_pass_rate))

    if p_e == 1:
        return None
    return (p_o - p_e) / (1 - p_e)


def test_judge_human_agreement_kappa():
    threshold = eligibility_decision_correctness.threshold
    pairs = []
    skipped = []

    for case in EXPENSE_ELIGIBILITY_CASES:
        label = JUDGE_CALIBRATION_LABELS.get(case["name"], {})
        human_score = label.get("human_score")
        if human_score is None:
            skipped.append(case["name"])
            continue

        chat_history = [SYSTEM_PROMPT]
        _, reply, trace = run_agent_turn(
            chat_history, case["input"], user_role=case["user_role"], employee_id=1)
        retrieval_context = [chunk["text"] for chunk in trace["retrieved_chunks"]]
        if not retrieval_context:
            skipped.append(case["name"])
            continue

        test_case = LLMTestCase(
            input=case["input"], actual_output=reply, retrieval_context=retrieval_context)
        judge_score = eligibility_decision_correctness.measure(
            test_case, _show_indicator=False)

        # Cohen's kappa needs categorical, not continuous, labels — reuse the
        # metric's own pass/fail threshold rather than inventing a separate one.
        pairs.append((human_score >= threshold, judge_score >= threshold))

    if len(pairs) < KAPPA_MIN_LABELS:
        pytest.skip(
            f"Only {len(pairs)}/{len(EXPENSE_ELIGIBILITY_CASES)} labeled+scoreable "
            f"case(s) ({skipped} skipped) — too few for Cohen's kappa to mean anything"
        )

    kappa = cohen_kappa(pairs)
    if kappa is None:
        pytest.skip(
            f"Human and judge pass/fail labels have zero variance between them "
            f"on this run ({pairs}) — kappa is undefined without any chance-level "
            f"disagreement to measure against"
        )

    assert kappa >= KAPPA_THRESHOLD, (
        f"Cohen's kappa between judge and human pass/fail labels (threshold="
        f"{threshold}) is {kappa:.3f} (< {KAPPA_THRESHOLD}) across {len(pairs)} "
        f"cases: {pairs}"
    )
