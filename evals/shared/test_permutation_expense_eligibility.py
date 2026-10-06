import numpy as np
import pytest
from scipy.stats import permutation_test
from deepeval.test_case import LLMTestCase

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.cases.expense_eligibility import EXPENSE_ELIGIBILITY_CASES
from evals.shared.cases.expense_eligibility_paraphrases import EXPENSE_ELIGIBILITY_PARAPHRASES
from evals.deepeval.metrics.eligibility_decision import eligibility_decision_correctness

REPETITIONS = 10
ALPHA = 0.05
MIN_PAIRS = 2


def _eligibility_score(user_role: str, message: str) -> float | None:
    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history, message, user_role=user_role, employee_id=1)
    retrieval_context = [chunk["text"] for chunk in trace["retrieved_chunks"]]

    if not retrieval_context:
        # The agent occasionally skips the search_hr_documents tool call
        # entirely for a given run — a real behavioral inconsistency in its
        # own right, but not one this test is measuring. Without retrieved
        # policy text the GEval judge would be scoring correctness against no
        # ground truth, so the pair is dropped rather than forced into a
        # meaningless score.
        return None

    test_case = LLMTestCase(
        input=message,
        actual_output=reply,
        retrieval_context=retrieval_context,
    )
    return eligibility_decision_correctness.measure(test_case, _show_indicator=False)


def _mean_paired_difference(x, y, axis):
    return np.mean(x - y, axis=axis)


def test_paraphrase_has_no_significant_effect_on_eligibility_score():
    original_scores = []
    paraphrase_scores = []
    dropped_pairs = 0

    for case in EXPENSE_ELIGIBILITY_CASES:
        paraphrase = EXPENSE_ELIGIBILITY_PARAPHRASES[case["name"]]

        for _ in range(REPETITIONS):
            original_score = _eligibility_score(
                case["user_role"], case["input"])
            paraphrase_score = _eligibility_score(
                case["user_role"], paraphrase)

            if original_score is None or paraphrase_score is None:
                dropped_pairs += 1
                continue

            original_scores.append(original_score)
            paraphrase_scores.append(paraphrase_score)

    total_pairs = REPETITIONS * len(EXPENSE_ELIGIBILITY_CASES)
    if len(original_scores) < MIN_PAIRS:
        pytest.skip(
            f"Only {len(original_scores)}/{total_pairs} pairs had retrieval "
            f"context on both sides ({dropped_pairs} dropped) — too few to run "
            f"a permutation test"
        )

    # Paired permutation (sign-flip) test: under the null hypothesis that
    # paraphrasing has no systematic effect, the assignment of a pair's two
    # scores to "original" vs "paraphrase" is exchangeable. No normality or
    # symmetry assumption is required, unlike a paired t-test or Wilcoxon
    # signed-rank test — well suited to bounded, judge-scored [0, 1] values.
    result = permutation_test(
        (original_scores, paraphrase_scores),
        _mean_paired_difference,
        permutation_type="samples",
        alternative="two-sided",
        n_resamples=9999,
        random_state=42,
    )

    mean_original = sum(original_scores) / len(original_scores)
    mean_paraphrase = sum(paraphrase_scores) / len(paraphrase_scores)

    assert result.pvalue > ALPHA, (
        f"Permutation test detected a significant effect of paraphrasing on the "
        f"eligibility decision score (p={result.pvalue:.4f} <= {ALPHA}): "
        f"mean original={mean_original:.3f}, mean paraphrase={mean_paraphrase:.3f} "
        f"({len(original_scores)}/{total_pairs} pairs used, {dropped_pairs} dropped "
        f"for missing retrieval context)"
    )
