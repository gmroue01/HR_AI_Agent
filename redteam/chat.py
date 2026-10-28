

from chatbot_core import run_agent_turn, SYSTEM_PROMPT


def call_api(prompt, options, context):
    chat_history = [SYSTEM_PROMPT]
    _, reply, _ = run_agent_turn(
        chat_history, prompt,
        user_role="employee", employee_id=1,
    )
    return {"output": reply}
