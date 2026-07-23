import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, ToolCall

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.conftest import trace_to_tool_calls
from evals.deepeval.datasets.task_completion_cases import TASK_COMPLETION_CASES
from evals.deepeval.metrics.task_completion import task_completion


@pytest.mark.parametrize("case", TASK_COMPLETION_CASES, ids=lambda c: c["name"])
def test_task_completion_case(case):
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
        additional_metadata={"task": case["task"]},
    )

    assert_test(test_case, [task_completion])
