import pytest
from agentevals.trajectory.match import create_trajectory_match_evaluator

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.cases.expense_eligibility import EXPENSE_ELIGIBILITY_CASES

strict_trajectory_match = create_trajectory_match_evaluator(
    trajectory_match_mode="strict",
    # Tool call arguments aren't part of what "trajectory" means here — the
    # metric already asserted elsewhere (ToolCorrectnessMetric, McNemar,
    # metamorphic) is whether the right tools fire, not with what arguments.
    tool_args_match_mode="ignore",
)


def _trajectory_messages(user_message: str, tool_names: list[str], final_content: str = "") -> list[dict]:
    """
    Build a minimal OpenAI-format message list from a flat, ordered list of
    tool names, one assistant/tool message pair per call. AgentEvals' strict
    mode compares trajectories message-by-message at fixed positions, so this
    shape — rather than the raw chat_history, whose round-grouping (how many
    tool calls land in the same assistant turn) is not something either side
    can predict in advance — is what makes the actual and reference
    trajectories structurally comparable regardless of how the real
    conversation happened to batch its tool calls.
    """
    messages = [{"role": "user", "content": user_message}]
    for name in tool_names:
        messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": name, "arguments": "{}"}}],
        })
        messages.append({"role": "tool", "content": ""})
    messages.append({"role": "assistant", "content": final_content})
    return messages


def _drop_optional_calls(tool_names: list[str], optional_tools: set[str]) -> list[str]:
    """
    AgentEvals ships strict (exact sequence), unordered/subset/superset (no
    order at all) — nothing in between for "these specific tools in this
    order, plus optionally anything from an allow-list, anywhere". Rather
    than lose order-checking by switching the whole case to superset mode,
    filter tolerated optional calls out before strict mode ever sees them —
    AgentEvals still does the real order comparison, just on the trajectory
    with optional noise removed.
    """
    return [name for name in tool_names if name not in optional_tools]


@pytest.mark.parametrize("case", EXPENSE_ELIGIBILITY_CASES, ids=lambda c: c["name"])
def test_agent_follows_the_expected_tool_trajectory(case):
    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history, case["input"], user_role=case["user_role"], employee_id=1)

    expected_tools = case["expected_tools"]
    optional_tools = set(case.get("optional_tools", []))
    actual_tool_names = [call["name"] for call in trace["tools_called"]]

    # 1. No call outside the required + tolerated sets — a genuinely
    #    unexpected tool (neither required nor explicitly optional) still
    #    fails, same as before.
    allowed_tools = set(expected_tools) | optional_tools
    unexpected = [name for name in actual_tool_names if name not in allowed_tools]
    assert not unexpected, (
        f"Unexpected tool call(s) for '{case['name']}': {unexpected} — not in "
        f"expected_tools {expected_tools} or optional_tools {sorted(optional_tools)}"
    )

    # 2. The required tools, with any tolerated optional calls filtered out,
    #    must still appear in the exact expected order.
    required_only = _drop_optional_calls(actual_tool_names, optional_tools)
    outputs = _trajectory_messages(case["input"], required_only, reply)
    reference_outputs = _trajectory_messages(case["input"], expected_tools)

    result = strict_trajectory_match(
        outputs=outputs, reference_outputs=reference_outputs)

    assert result["score"], (
        f"Trajectory mismatch for '{case['name']}': agent called "
        f"{actual_tool_names} (required tools, optional calls filtered out: "
        f"{required_only}) but the expected trajectory is {expected_tools} "
        f"(order matters — search_hr_documents must precede submit_expense, "
        f"since eligibility has to be checked before an expense can be submitted)"
    )
