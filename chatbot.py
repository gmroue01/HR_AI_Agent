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
    """Filtre les arguments pour ne garder que les clés attendues par le schéma du tool.
    Corrige les quirks de génération de certains modèles (ex: {'data': {}} ou {'': {}}
    au lieu de {} quand le tool n'a aucun paramètre)."""
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
system_prompt = {
    "role": "system",
    "content": (
        "You are an HR assistant with access to the company's employee database "
        "through function calling. You must NEVER write code or describe function "
        "calls as text. Instead, use the native tool calling mechanism provided by "
        "the API. When a user asks about employee data, invoke the appropriate tool directly."
    )
}
chat_history = [system_prompt]

while True:
    user_input = input("User: ")

    if user_input.lower() in ("exit", "quit", "q"):
        print("Fin de la conversation.")
        break

    chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        messages=chat_history,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    assistant_message = {"role": "assistant",
                         "content": response_message.content}
    if tool_calls:
        assistant_message["tool_calls"] = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
            }
            for tc in tool_calls
        ]
    chat_history.append(assistant_message)

    if tool_calls:
        for tool_call in tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            fn_args = clean_tool_args(
                fn_name, fn_args, TOOLS_SCHEMA)  
            print("DEBUG fn_args:", repr(fn_args))

            if fn_name not in AVAILABLE_FUNCTIONS:
                results = {"error": f"Fonction inconnue: {fn_name}"}
            else:
                try:
                    results = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
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
            model=MODEL,
            messages=chat_history,
            tools=TOOLS_SCHEMA,
            tool_choice="none"
        )
        final_message = final_response.choices[0].message
        chat_history.append(
            {"role": "assistant", "content": final_message.content})
        print("Assistant:", final_message.content)
    else:
        print("Assistant:", response_message.content)

    if len(chat_history) > MAX_HISTORY_MESSAGES:
        chat_history = [chat_history[0]] + \
            chat_history[-(MAX_HISTORY_MESSAGES - 1):]
