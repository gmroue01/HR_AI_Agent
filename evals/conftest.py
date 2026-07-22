from deepeval.test_case import ToolCall


def trace_to_tool_calls(trace: dict) -> list[ToolCall]:
    """"
    Transform the trace dict into a list of TooCall deepeval object

    Args:
        trace (dict) : the agent trace
    return: 
        list[ToolCall] : the list with all the corresponding ToolCall object.
    Raises:
        None

    """
    return [
        ToolCall(name=t["name"], input_parameters=t["arguments"])
        for t in trace["tools_called"]
    ]
