# Architecture

This document explains and details all the technical aspects and choices of the chatbot part.

## `/chatbot`

This folder contains all the chatbot logic.

### `chatbot.py`

#### Initialization

The script initializes the following components:

**API key**

```python
API_KEY = os.environ.get("GROQ_API_KEY")
```

`API_KEY` (`str`, constant) — the private Groq API key, stored in the `.env` file under `GROQ_API_KEY`.

**Groq client**

```python
client = Groq(api_key=API_KEY)
```

`client` (`Groq` object) — the entry point to the Groq API. It exposes methods to forward user prompts to a chosen model.

**System prompt**

`system_prompt` is a Python dictionary (JSON format) that defines the chatbot's default behavior:

```python
system_prompt = {
    "role": "system",
    "content": "..."
}
```

See [PROMPT_SYSTEM.md](./PROMPT_SYSTEM.md) for details on how this is defined.

**Chat history**

```python
chat_history = [system_prompt]
```

`chat_history` (`List[dict]`) — a list of JSON-formatted messages (role/content pairs) that stores the full conversation, starting with the system prompt.

#### Main loop

The script runs a loop that waits for user input:

```python
user_input = input("User: ")
```

Each user message is appended to `chat_history`:

```python
chat_history.append({"role": "user", "content": user_input})
```

See [PROMPT_JSON_FORMAT.md](./PROMPT_JSON_FORMAT.md) for details on the JSON message format.

The full `chat_history` (including the system prompt) is sent to the model via `client.chat.completions.create()`:

```python
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=chat_history
)
```

Required parameters:
- `model` (`str`) — the Groq model to use.
- `messages` (`List[dict]`) — the conversation history sent to the model for generating a response.

The method returns a `ChatCompletion` object. See the [Groq API reference](https://console.groq.com/docs/api-reference#chat-create) for details.

The assistant's response is appended to `chat_history`, then printed to the console.

