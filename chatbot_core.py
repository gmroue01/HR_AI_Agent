import os
from dotenv import load_dotenv
import json
from groq import Groq
from tools.schemas import TOOLS_SCHEMA
from tools.dispatcher import AVAILABLE_FUNCTIONS

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

MODEL = "openai/gpt-oss-120b"
MAX_HISTORY_MESSAGES = 20


def clean_tool_args(fn_name: str, fn_args: dict, tools_schema: list) -> dict:
    """
    Filter all args in order to only keep the expected key from the tool schema.

    Parameters : 

    fn_name : tool's name.
    fn_args : tool's args.
    tools_schema : a JSON list of tools avalaible for the agent.

    """
    schema = next(
        (t["function"]["parameters"]
         for t in tools_schema if t["function"]["name"] == fn_name),
        {}
    )
    expected_keys = set(schema.get("properties", {}).keys())

    if not expected_keys:
        return {}

    return {k: v for k, v in fn_args.items() if k in expected_keys}


# TODO : Connect the real system prompt file.
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are an HR assistant with access to: (1) the employee database via "
        "function calling, and (2) the company's HR policy documents via semantic "
        "search. Use search_hr_documents when the user asks about policies, "
        "procedures, or benefits. Use get_all_employees for employee data queries. "
        "Always ground your answers in the retrieved information rather than "
        "general knowledge, and mention which source document the information "
        "came from when available. Answer shortly and precisely."
    )
}


def run_agent_turn(chat_history: list, user_message: str, user_role: str) -> tuple[list, str]:
    chat_history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL, messages=chat_history,
        tools=TOOLS_SCHEMA, tool_choice="auto"
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    assitant_message = {"role": "assistant",
                        "content": response_message.content}

    if tool_calls:
        assitant_message["tool_calls"] = [
            {"id": tc.id, "type": tc.type, "function": {
                "name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in tool_calls
        ]

    chat_history.append(assitant_message)

    if not tool_calls:
        return chat_history, response_message.content

    for tool_call in tool_calls:
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)
        fn_args = clean_tool_args(fn_name, fn_args, TOOLS_SCHEMA)

        if fn_name not in AVAILABLE_FUNCTIONS:
            results = {"error": f"Fonction inconnue: {fn_name}"}
        else:
            try:
                results = AVAILABLE_FUNCTIONS[fn_name](
                    **fn_args, user_role=user_role)
            except Exception as e:
                results = {"error": str(e)}
                print("DEBUG ERROR:", e)

        chat_history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": fn_name,
            "content": json.dumps(results, default=str)
        })

    final_response = client.chat.completions.create(
        model=MODEL, messages=chat_history, tools=TOOLS_SCHEMA, tool_choice="none"
    )

    final_message = final_response.choices[0].message
    chat_history.append(
        {"role": "assistant", "content": final_message.content})

    return chat_history, final_message.content
