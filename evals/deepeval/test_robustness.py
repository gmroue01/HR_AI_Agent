# evals/test_robustness.py
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.deepeval.conftest import trace_to_tool_calls
from evals.deepeval.datasets.robustness_cases import ROBUSTNESS_CASES
from evals.deepeval.metrics.robustness import robustness_metric


@pytest.mark.parametrize("case", ROBUSTNESS_CASES, ids=lambda c: c["name"])
def test_robustness_case(case):
    chat_history = [SYSTEM_PROMPT]

    updated_history, reply, trace = run_agent_turn(
        chat_history,
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=reply,
        tools_called=trace_to_tool_calls(trace),
    )

    assert_test(test_case, [robustness_metric])
