The objective of this document introduce the trace system of the application, that is the heart of the test architecture.



## Trace.

A trace is a sign that something has happened or existed.

In this context, `trace` is a dict variable which is assigned two elements :
    **`"tool_called"`**: list that contains a specific json structure. The json defines the `name` of the tools, the `arguments` of the tools and the `result` value of tool function.
    **`"retrieved_chunks"`** : contents retrieved throught any RAG call. These contents are appended to the `result` value.

The `trace` variable is assigned after any tool calls from the model in the [`chatbot_core.py`] (../chatbot_core.py) which implements the agent logic.


## Trace in test.

The `trace` is used in any test which LLM as judge is required. It is mandatory to use as the LLM as judge is able to understand what the models did exactly.

`DeepEval` implements this logic via the `LLMTestCase` object which has the `tool_called` parameter. 

This argument requires a specific variable type called `ToolCall`. 

That's why we implement a `trace-into-TooCall` translator as a function `trace_to_tool_calls()`in the [`conftest.py`](../evals/conftest.py) script.

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




