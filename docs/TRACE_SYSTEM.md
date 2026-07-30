The objective of this document introduce the trace system of the application, that is the heart of the test architecture.



## Trace.

A trace is a sign that something has happened or existed.

In this context, `trace` is a dict variable which is assigned two elements :
    **`"tools_called"`**: list that contains a specific json structure. The json defines the `name` of the tools, the `arguments` of the tools and the `result` value of tool function.
    **`"retrieved_chunks"`** : contents retrieved throught any RAG call. These contents are appended to the `result` value.

The `trace` variable is assigned after any tool calls from the model in the [`chatbot_core.py`] (../chatbot_core.py) which implements the agent logic.


## Trace in test.

The `trace` is used in any test which LLM as judge is required. It is mandatory to use as the LLM as judge is able to understand what the models did exactly.

`DeepEval` implements this logic via the `LLMTestCase` object which has the `tool_called` parameter. 

This argument requires a specific variable type called `ToolCall`. 

That's why we implement a `trace-into-TooCall` translator as a function `trace_to_tool_calls()`in the [`conftest.py`](../evals/shared/conftest.py) script.

## Reproducible tests : resetting state between runs

Tests that touch the expense flow need `employee_id=1`'s `expense_amount` to start at 0 every time, regardless of the order tests run in or of manual testing done beforehand through Streamlit. `reset_test_employee_expense()`, an `autouse` pytest fixture in [`conftest.py`](../evals/shared/conftest.py), does this reset before every test.

For this fixture to actually run, pytest needs to discover it — and pytest only auto-loads a `conftest.py` from a test file's own directory and its *ancestor* directories, not from a sibling one. `evals/shared/` is a sibling of `evals/deepeval/` and `evals/trulens/`, not their ancestor, so a fixture defined only there would never fire for either framework's tests. [`evals/conftest.py`](../evals/conftest.py) — a parent of both — re-exports it :

```python
from evals.shared.conftest import reset_test_employee_expense  # noqa: F401
```

This one-line file is what makes the fixture apply to every test under `evals/`, DeepEval and TruLens alike, without either framework needing its own copy.

## Trace in a test case example

```python
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
```




