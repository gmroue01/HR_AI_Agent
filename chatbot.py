import os
from dotenv import load_dotenv
import json
from groq import Groq
from tools.schemas import TOOLS_SCHEMA
from tools.dispatcher import AVAILABLE_FUNCTIONS

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

MODEL = "llama-3.3-70b-versatile"  # même modèle pour les deux appels
MAX_HISTORY_MESSAGES = 20  # garde-fou basique pour les tokens

# TODO : Connect the real system prompt file.
system_prompt = {
    "role": "system",
    "content": "You are a helpful assistant that answers questions about HR policies and procedures."
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

    # on ajoute toujours le message assistant complet (avec tool_calls si présents)
    chat_history.append(response_message.model_dump())

    if tool_calls:
        for tool_call in tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            if fn_name not in AVAILABLE_FUNCTIONS:
                results = {"error": f"Fonction inconnue: {fn_name}"}
            else:
                try:
                    results = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
                except Exception as e:
                    results = {"error": str(e)}

            chat_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": fn_name,
                "content": json.dumps(results, default=str)
            })

        # un seul appel final, APRÈS avoir traité tous les tool_calls
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=chat_history
        )
        final_message = final_response.choices[0].message
        chat_history.append(final_message.model_dump())
        print("Assistant:", final_message.content)
    else:
        print("Assistant:", response_message.content)

    # garde-fou simple : tronque l'historique si trop long (garde le system prompt)
    if len(chat_history) > MAX_HISTORY_MESSAGES:
        chat_history = [chat_history[0]] + \
            chat_history[-(MAX_HISTORY_MESSAGES - 1):]
