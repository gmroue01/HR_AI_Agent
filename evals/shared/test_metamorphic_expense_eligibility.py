import pytest

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.cases.expense_eligibility import EXPENSE_ELIGIBILITY_CASES
from evals.shared.cases.expense_eligibility_paraphrases import EXPENSE_ELIGIBILITY_PARAPHRASES


def _tools_called(user_role: str, message: str) -> set[str]:
    chat_history = [SYSTEM_PROMPT]
    _, _, trace = run_agent_turn(
        chat_history, message, user_role=user_role, employee_id=1)
    return {call["name"] for call in trace["tools_called"]}


@pytest.mark.parametrize("case", EXPENSE_ELIGIBILITY_CASES, ids=lambda c: c["name"])
def test_paraphrase_does_not_change_the_tools_called(case):
    paraphrase = EXPENSE_ELIGIBILITY_PARAPHRASES[case["name"]]

    original_tools = _tools_called(case["user_role"], case["input"])
    paraphrased_tools = _tools_called(case["user_role"], paraphrase)

    assert original_tools == paraphrased_tools, (
        f"Rewording changed which tools were called for '{case['name']}': "
        f"original={original_tools} vs paraphrase={paraphrased_tools}"
    )
