## `chatbot_core.py` — Agent turn flow

This module orchestrates one full "turn" of the HR agent: receiving a user message, 
letting the model decide whether to call tools, executing them, and producing a 
final answer. Tool declaration and execution details are covered in 
[`tool-calling.md`](./tool-calling.md); this section covers the surrounding flow.

### `run_agent_turn(chat_history, user_message, user_role, employee_id=None)`

Runs up to `max_round` (5) rounds of model calls:

1. The user message is sent to the model along with `TOOLS_SCHEMA` (`tool_choice="auto"`).
2. If the model's response contains no tool calls, its content is returned immediately 
   as the final answer.
3. If it does, each tool is executed (see `tool-calling.md`) with `user_role` and 
   `employee_id` passed through — these scope what data the tool is allowed to return, 
   in line with the project's authorization matrix.
4. The tool results are appended to `chat_history` as `tool` messages, and the loop 
   repeats: the model sees the results and can either answer or request further tools.

This means chained tool calls are supported (e.g. look up an employee, then search a 
policy document, then answer) — not just a single tool-call round-trip.

### Round limit safeguard

If the model still hasn't produced a final answer after `max_round` rounds, one last 
call is made with `tool_choice="none"`, forcing the model to answer using only the 
information already gathered, without requesting further tools. This guarantees the 
function always terminates with a text response.

### `clean_tool_args(fn_name, fn_args, tools_schema)`

Filters the arguments returned by the model down to only the keys declared in that 
tool's schema (`properties`), dropping anything the model may have hallucinated or 
added incorrectly. Returns an empty dict if the tool isn't found in the schema.

### System prompt

`SYSTEM_PROMPT` is currently defined inline in this file as a placeholder 
(see the `TODO` in the source) — it is not yet loaded from an external prompt file.

