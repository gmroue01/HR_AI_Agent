import pytest
from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.conftest import trace_to_tool_calls
from evals.deepeval.datasets.confidential_access_cases import CONFIDENTIAL_ACCESS_CASES
from evals.deepeval.metrics.refusal_correctness import refusal_correctness
from evals.deepeval.groq_judge import GroqJudge


groq_judge = GroqJudge()


@pytest.mark.parametrize("case", CONFIDENTIAL_ACCESS_CASES, ids=lambda c: c["name"])
def test_confidential_access_case(case):
    chat_history = [SYSTEM_PROMPT]
    updated_history, reply, trace = run_agent_turn(
        chat_history,
        case["input"],
        user_role=case["user_role"],
        employee_id=1
    )

    actual_tools_called = trace_to_tool_calls(trace)
    expected_tools = [ToolCall(name=name) for name in case["expected_tools"]]

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=reply,
        tools_called=actual_tools_called,
        expected_tools=expected_tools
    )

    tool_metric = ToolCorrectnessMetric(threshold=1.0, model=groq_judge)

    assert_test(test_case, [tool_metric, refusal_correctness])
