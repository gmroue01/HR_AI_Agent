# Tool Calling Flow

## 1. Declaring the tools to the model

On every API agent call in [`chatbot_core.py`](../chatbot_core.py), the `TOOLS_SCHEMA` from 
[`schemas.py`](../tools/schemas.py) is passed to describe the available functions the agent 
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


### Filtering the SDK response
The `tool_calls` object returned by the SDK includes fields beyond what the API accepts 
back as input. Applying `model_dump()` directly would resend unsupported fields. Instead, 
the script extracts only [id, type, function.name, function.arguments] before appending 
to chat_history.

## 3. Mapping tool names to Python functions

The [`dispatcher.py`](../tools/dispatcher.py) script maps the functions referred to by the models in `TOOLS_SCHEMA` to their corresponding Python functions.

It keeps a list of functions available to the agent, called `AVAILABLE_FUNCTION`.

In the main script, this list is always checked before any function is called.

The script [`employee_service.py`](../backend/services/employee_service.py) implements all the logic behind any of the available tools.

The script `database.py` contains the database connection logic.

These functions are the only ones required to allow the agent to access tools.

## 4. Second call — sending results back to the model

Once every tool call has been executed and its result appended to `chat_history` 
(see [`CHATBOT.md`](./CHATBOT.md)), the full conversation — the 
original user prompt, the assistant's tool call decision, and each tool's result — 
is sent back to the model in a second call to `client.chat.completions.create()`.

At this point `chat_history` contains, in order:
- the original `system` and `user` messages,
- the `assistant` message recorded in step 2 (the model's tool call decision),
- one `tool` message per executed function, holding its result (see step 3).

The model uses this full context to generate its final answer, incorporating the 
tools' return values. This response is a normal assistant message — no further tool 
calls are expected unless the model requests them again (e.g. chained tool calls).


