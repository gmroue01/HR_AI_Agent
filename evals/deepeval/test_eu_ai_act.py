import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.conftest import trace_to_tool_calls
from evals.deepeval.datasets.eu_ai_act_cases import EU_AI_ACT_CASES
from evals.deepeval.metrics.eu_ai_act import eu_ai_act_compliance


@pytest.mark.parametrize("case", EU_AI_ACT_CASES, ids=lambda c: c["name"])
def test_eu_ai_act_case(case):
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

    assert_test(test_case, [eu_ai_act_compliance])
