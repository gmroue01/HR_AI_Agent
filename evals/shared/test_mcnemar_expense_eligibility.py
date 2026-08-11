from scipy.stats import binomtest
import pytest

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.cases.expense_eligibility import EXPENSE_ELIGIBILITY_CASES
from evals.shared.cases.expense_eligibility_paraphrases import EXPENSE_ELIGIBILITY_PARAPHRASES

REPETITIONS = 10
ALPHA = 0.05


def _is_correct(user_role: str, message: str, expected_tools: set[str]) -> bool:
    chat_history = [SYSTEM_PROMPT]
    _, _, trace = run_agent_turn(
        chat_history, message, user_role=user_role, employee_id=1)
    tools_called = {call["name"] for call in trace["tools_called"]}
    return tools_called == expected_tools


def test_paraphrase_has_no_significant_effect_on_correctness():
    both_correct = original_only = paraphrase_only = both_wrong = 0

    for case in EXPENSE_ELIGIBILITY_CASES:
        expected_tools = set(case["expected_tools"])
        paraphrase = EXPENSE_ELIGIBILITY_PARAPHRASES[case["name"]]

        for _ in range(REPETITIONS):
            original_correct = _is_correct(
                case["user_role"], case["input"], expected_tools)
            paraphrase_correct = _is_correct(
                case["user_role"], paraphrase, expected_tools)

            if original_correct and paraphrase_correct:
                both_correct += 1
            elif original_correct and not paraphrase_correct:
                original_only += 1
            elif paraphrase_correct:
                paraphrase_only += 1
            else:
                both_wrong += 1

    discordant = original_only + paraphrase_only
    if discordant == 0:
        pytest.skip(
            "No discordant pairs across all trials: original and paraphrase always "
            "agreed, McNemar's test is undefined without disagreement to measure"
        )

    # McNemar's exact test is a two-sided binomial test on the discordant pairs
    # against the null hypothesis that a disagreement is equally likely to favor
    # either condition (p=0.5) — i.e. paraphrasing has no systematic effect.
    p_value = binomtest(original_only, discordant, 0.5,
                         alternative="two-sided").pvalue

    assert p_value > ALPHA, (
        f"McNemar's test detected a significant effect of paraphrasing on correctness "
        f"(p={p_value:.4f} <= {ALPHA}): original-only-correct={original_only}, "
        f"paraphrase-only-correct={paraphrase_only} out of {discordant} discordant pairs "
        f"({both_correct} agreed-correct, {both_wrong} agreed-incorrect, "
        f"{REPETITIONS} repetitions x {len(EXPENSE_ELIGIBILITY_CASES)} cases)"
    )
