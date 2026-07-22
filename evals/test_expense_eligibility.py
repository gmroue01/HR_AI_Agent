import pytest
from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.conftest import trace_to_tool_calls
from evals.datasets.expense_eligibility_cases import EXPENSE_ELIGIBILITY_CASES
from evals.metrics.faithfulness import expense_faithfulness
from evals.metrics.eligibility_decision import eligibility_decision_correctness
from evals.groq_judge import GroqJudge

groq_judge = GroqJudge()


@pytest.mark.parametrize("case", EXPENSE_ELIGIBILITY_CASES, ids=lambda c: c["name"])
def test_expense_eligibility_case(case):
    chat_history = [SYSTEM_PROMPT]

    updated_history, reply, trace = run_agent_turn(
        chat_history,
        case["input"],
        user_role=case["user_role"],
        employee_id=1,
    )

    actual_tools_called = trace_to_tool_calls(trace)
    expected_tools = [ToolCall(name=name) for name in case["expected_tools"]]
    retrieval_context = [chunk["text"] for chunk in trace["retrieved_chunks"]]

    assert retrieval_context, (
        f"No RAG context retrieved for case '{case['name']}' — "
        f"cannot evaluate faithfulness without retrieved chunks"
    )

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=reply,
        tools_called=actual_tools_called,
        expected_tools=expected_tools,
        retrieval_context=retrieval_context,
    )

    tool_metric = ToolCorrectnessMetric(threshold=1.0, model=groq_judge)

    assert_test(test_case, [
                tool_metric, expense_faithfulness, eligibility_decision_correctness])
