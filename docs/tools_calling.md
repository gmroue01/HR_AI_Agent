This document shall describe how tool agent calls work.

# Step by Step:

## 1. Declaring the tools to the model

On every API agent call in [`chatbot.py`](../chatbot.py), the `TOOLS_SCHEMA` from 
[`schema.py`](../tools/schema.py) is passed to describe the available functions the agent 
can call.

`TOOLS_SCHEMA` is a list of objects, each containing the following fields:

- `type`: Tells the API this entry describes a callable tool (always `"function"`).
- `function`: Wraps the function description (name, description, parameters).
- `function.name`: The name of the function, as it must be called by the agent.
- `function.description`: The function's purpose — used by the model to decide when to call it.
- `function.parameters`: A JSON Schema object describing the arguments the function accepts.

```json
{
    "type": "function",
    "function": {
        "name": "get_all_employees",
        "description": "Return a list of all registered employees",
        "parameters": {"type": "object", "properties": {}}
    }
}

```

## 2. First call - the model decides

In the `client` API Agent parameters, the `tool_choice` parameter provides the way that the model chooses the proper tools in relation to the context.

The `tool_choice` parameter is defined as `auto`. The model shall be able to choose the right tool by itself.

Compared to the user's prompt, the API response returns the model-selected tools as a `tool_calls` variable if tools are required.

If the `tool_calls` variable is not empty, the script records the model-selected tools along with the results of those selected functions.

This information must be sent back to the model so it can generate the complete answer, including the return values of the model-selected functions.

The `tool_calls` is an SDK object that includes more fields than the API entrypoint should accept. Instead of applying a simple `model_dump()`, the script uses the subset of arguments accepted by the API as a response.

## How to reference the Python functions

The [`dispatcher.py`](https://www.google.com/search?q=../tools/dispatcher.py) script maps the functions referred to by the models in `TOOLS_SCHEMA` to their corresponding Python functions.

It keeps a list of functions available to the agent, called `AVAILABLE_FUNCTION`.

In the main script, this list is always checked before any function is called.

The script [`employee_service.py`](https://www.google.com/search?q=../services/employee_service.py) implements all the logic behind any of the available tools.

The script `database.py` contains the database connection logic.

These functions are the only ones required to allow the agent to access tools.

