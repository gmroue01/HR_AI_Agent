"""
Demonstrates mocking the LLM agent: chatbot_core.run_agent_turn() is tested
without any real Groq API call, by replacing client.chat.completions.create
with a canned response. This makes the tests free, instant, and deterministic,
at the cost of not verifying anything about real model behavior.
"""
import json
from types import SimpleNamespace

import chatbot_core


def make_response(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


def make_tool_call(call_id: str, name: str, arguments: dict):
    function = SimpleNamespace(name=name, arguments=json.dumps(arguments))
    return SimpleNamespace(id=call_id, type="function", function=function)


def test_returns_direct_reply_when_model_calls_no_tool(monkeypatch):
    monkeypatch.setattr(
        chatbot_core.client.chat.completions, "create",
        lambda **kwargs: make_response(content="Hello! How can I help?"),
    )

    history = [chatbot_core.SYSTEM_PROMPT]
    updated_history, reply, trace = chatbot_core.run_agent_turn(
        history, "Hi", user_role="employee", employee_id=1
    )

    assert reply == "Hello! How can I help?"
    assert updated_history[-1] == {"role": "assistant", "content": "Hello! How can I help?"}
    assert trace["tools_called"] == []


def test_calls_a_tool_then_returns_the_final_reply(monkeypatch):
    responses = [
        make_response(tool_calls=[make_tool_call("call_1", "get_my_info", {})]),
        make_response(content="You earn 5000 and you are healthy."),
    ]

    def fake_create(**kwargs):
        return responses.pop(0)

    monkeypatch.setattr(chatbot_core.client.chat.completions, "create", fake_create)
    monkeypatch.setattr(
        chatbot_core, "AVAILABLE_FUNCTIONS",
        {"get_my_info": lambda **kwargs: {"salary": 5000, "wellness": "healthy"}},
    )

    history = [chatbot_core.SYSTEM_PROMPT]
    updated_history, reply, trace = chatbot_core.run_agent_turn(
        history, "What's my salary?", user_role="employee", employee_id=1
    )

    assert reply == "You earn 5000 and you are healthy."
    assert trace["tools_called"] == [{
        "name": "get_my_info",
        "arguments": {},
        "result": {"salary": 5000, "wellness": "healthy"},
    }]
    tool_message = next(m for m in updated_history if m.get("role") == "tool")
    assert json.loads(tool_message["content"]) == {"salary": 5000, "wellness": "healthy"}


def test_unknown_tool_call_is_recorded_as_an_error_without_crashing(monkeypatch):
    responses = [
        make_response(tool_calls=[make_tool_call("call_1", "does_not_exist", {})]),
        make_response(content="Sorry, I can't do that."),
    ]
    monkeypatch.setattr(
        chatbot_core.client.chat.completions, "create",
        lambda **kwargs: responses.pop(0),
    )
    monkeypatch.setattr(chatbot_core, "AVAILABLE_FUNCTIONS", {})

    history = [chatbot_core.SYSTEM_PROMPT]
    _, reply, trace = chatbot_core.run_agent_turn(
        history, "Do the impossible", user_role="employee", employee_id=1
    )

    assert reply == "Sorry, I can't do that."
    assert trace["tools_called"][0]["result"] == {"error": "Fonction inconnue: does_not_exist"}
