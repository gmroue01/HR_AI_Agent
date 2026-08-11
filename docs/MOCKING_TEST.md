This document gathers the test function documentation for the mocked-agent suite in [`tests/`](../tests/).

Every other suite in this project (DeepEval, TruLens, Opik, and the Playwright E2E suite — see [`PLAYWRIGHT_TEST.md`](./PLAYWRIGHT_TEST.md)) calls the real Groq API and either judges the answer with an LLM-as-a-judge or drives the real app end to end. This suite does the opposite : it replaces `chatbot_core.client.chat.completions.create` with a canned, hand-written response via `pytest`'s `monkeypatch`, so no network call happens at all.

That trade-off is deliberate. Mocking the model call means these tests are free, run in a few seconds instead of tens of seconds, and are fully deterministic — the same input always produces the same assertion result, since there is no real model sampling involved. In exchange, they verify nothing about the model's actual judgment or language quality — a mocked response of `"Hello! How can I help?"` never tells you whether the real model would say anything sensible. What they do verify is the orchestration logic in `chatbot_core.run_agent_turn()` around the model call : does the chat history get appended correctly, does a tool call get dispatched and its result recorded in `trace["tools_called"]`, does an unknown tool name fail gracefully instead of crashing. That logic is exact-match, deterministic Python — exactly the kind of thing a mock is suited to test, as opposed to the subjective, model-quality questions the LLM-as-a-judge suites are built for.

The mock itself is built from `types.SimpleNamespace`, shaped to match the attributes `run_agent_turn()` actually reads off a Groq response : `response.choices[0].message.content` and `response.choices[0].message.tool_calls` (a list of objects exposing `.id`, `.type`, and `.function.name` / `.function.arguments`). A `make_response()` / `make_tool_call()` helper pair builds these without pulling in the real `groq` response classes.

## [`test_chatbot_core.py`](../tests/test_chatbot_core.py)

**Objective** : Verify the agent loop in `chatbot_core.run_agent_turn()` handles the three shapes a model response can take, without ever calling the real API.

- **`test_returns_direct_reply_when_model_calls_no_tool`** — the mocked response has content and no `tool_calls`. Verifies the reply is returned as-is, the assistant message is appended to the history, and `trace["tools_called"]` stays empty.
- **`test_calls_a_tool_then_returns_the_final_reply`** — the first mocked response requests `get_my_info` (chosen because its schema takes no arguments, keeping the mock minimal), the second mocked response is the final reply. `chatbot_core.AVAILABLE_FUNCTIONS` is also monkeypatched to a stub, so the tool dispatch never touches the real SQLite database. Verifies the tool's result lands both in `trace["tools_called"]` and in the `role: "tool"` message added to the history, and that the reply after the tool round-trip is the second mocked response.
- **`test_unknown_tool_call_is_recorded_as_an_error_without_crashing`** — the mocked response asks for a tool name that doesn't exist in `AVAILABLE_FUNCTIONS`. Verifies `run_agent_turn()` records a `{"error": "Fonction inconnue: ..."}` result and continues to the final reply instead of raising.

Run with `pytest tests/test_chatbot_core.py -v`.
