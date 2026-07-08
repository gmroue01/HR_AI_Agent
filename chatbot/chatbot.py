import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

assert client is not None, "Failed to create Groq client. Please check your API key."

system_prompt = {
    "role": "system",
    "content": "You are a helpful assistant that answers questions about HR policies and procedures."
}

chat_history = [system_prompt]

while True:


    user_input = input("User: ")

    chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant", messages=chat_history)

    chat_history.append(
        {"role": "assistant", "content": response.choices[0].message.content})

    print("Assistant:", response.choices[0].message.content)
