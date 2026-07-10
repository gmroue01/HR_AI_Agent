## Git - "Refusing to merge unrelated histories"

**Context**: Push to the `main` branch failed.

```bash
(venv) PS C:\Users\gmrou\HR_AgentIA> git push origin main
To https://github.com/gmroue01/HR_AI_Agent.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/gmroue01/HR_AI_Agent.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g.
hint: 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

The push is rejected because the local branch is behind the remote branch.

**Hypothesis**: The local and remote repositories have unrelated histories — the GitHub repo was created with a README and `.gitignore` already committed remotely, while the local repo was initialized separately.

**Solution**:
```bash
git pull origin main --allow-unrelated-histories
```

**Why**: `--allow-unrelated-histories` forces Git to merge two histories that don't share a common ancestor (blocked by default as a safety measure).



# Debugging Log: Groq Tool Calling Integration (HR Agent)

## Context

**Component:** `chatbot.py` (agent orchestration layer) + `tools/dispatcher.py` (tool execution layer) + `backend/` (FastAPI + SQLite service layer)

**Goal:** Enable the Groq-hosted LLM to call local Python functions (tools) that query the HR SQLite database, following the standard OpenAI-compatible tool-calling pattern (`tools` + `tool_choice` + `tool_call_id` round-trip).

**Symptom:** A working single-turn chat (`Hello` → greeting) broke down as soon as a tool-requiring query was sent, producing a chain of distinct errors across several debugging iterations. Each fix exposed the next layer of the problem.

This document records the issues encountered, in the order they surfaced, their root causes, and the fixes applied. It's meant as a reference for similar agentic/tool-calling integrations built on this stack (FastAPI + SQLite + Groq).

---

## Issue 1 — Module import errors (`ModuleNotFoundError: No module named 'backend'`)

**Symptom:**
```
File "backend/main.py", line 2, in <module>
    from routers import employees
ModuleNotFoundError: No module named 'backend'
```

**Root cause:** Inconsistent import conventions across files. `backend/main.py` used a relative-style import (`from routers import employees`), assuming Python would be launched *from inside* `backend/`. Meanwhile, `backend/routers/employees.py` used an absolute import (`from backend.database import get_db`), assuming Python would be launched *from the project root*. These two conventions are mutually incompatible — only one can be true for a given `sys.path`.

Python resolves imports based on **where the process is launched from**, not where the files live on disk. The launch directory (plus installed packages) determines what's importable.

**Fix:**
- Standardized on **absolute imports from the project root** everywhere (`from backend.routers import employees`, `from backend.database import get_db`, etc.)
- Always launch commands from the project root:
  ```bash
  cd HR_AgentIA
  uvicorn backend.main:app --reload
  ```
- Added `__init__.py` to every package directory (`backend/`, `backend/routers/`, `backend/services/`, `tools/`) to ensure they're recognized as importable packages.

**Lesson:** Pick one import convention (absolute-from-root) and enforce it project-wide. Mixing relative and absolute imports across sibling modules is a common source of `ModuleNotFoundError` that resurfaces differently depending on the current working directory at launch time.

---

## Issue 2 — Wrong FastAPI parameter name (`TypeError: 'ModelMetaclass' object is not a mapping`)

**Symptom:**
```python
@router.post("/", responses=EmployeeOut, status_code=201)
```
```
TypeError: 'ModelMetaclass' object is not a mapping
```

**Root cause:** Typo — `responses` (plural) is a *different* FastAPI parameter, used to document possible response codes for OpenAPI/Swagger (expects a `dict`). The intended parameter was `response_model` (singular), which expects a Pydantic model class.

**Fix:**
```python
@router.post("/", response_model=EmployeeOut, status_code=201)
```

**Lesson:** `response_model` vs `responses` is an easy typo to make and produces a cryptic error rather than a clear "unknown parameter" message, because both are valid FastAPI kwargs.

---

## Issue 3 — Malformed tool schema (`'tools.0.function' : value must be an object`)

**Symptom:**
```python
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": "get_all_employees",   # ❌ string instead of an object
        "description": "...",
        "parameters": {...}
    }
]
```
```
groq.BadRequestError: 'tools.0.function' : value must be an object
```

**Root cause:** Misunderstanding of the OpenAI-compatible tool schema nesting. `function` must be an **object** containing `name`, `description`, and `parameters` — not a bare string with the function name, with `description`/`parameters` as siblings.

**Fix:**
```python
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_all_employees",
            "description": "...",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]
```

**Lesson:** The tool schema has a fixed two-level nesting (`type` → `function` → `{name, description, parameters}`). Any deviation is rejected by the API with a schema-validation error rather than being silently corrected.

---

## Issue 4 — Model reasoning about tools instead of calling them (hallucinated tool use)

**Symptom:** After fixing the schema, the assistant's `content` contained descriptions or fabricated syntax instead of a real `tool_calls` entry:
```
Assistant: <function>get_all_employees()</function>
```
or Python-like pseudo-code describing how it *would* call the function.

**Root cause:** Combination of factors:
1. A vague system prompt that didn't clearly instruct the model to use the native tool-calling mechanism.
2. Assistant messages being re-injected into history via `response_message.model_dump()`, which serializes **all** SDK-internal fields (see Issue 5) — this can confuse the model on subsequent turns about what actually happened.
3. Underlying model behavior differences — smaller/deprecated models are less reliable at consistently emitting structured `tool_calls` versus describing them in text.

**Fix:**
- Rewrote the system prompt to explicitly state the model must never write or describe function calls as text, and must use the native tool-calling mechanism:
  ```python
  system_prompt = {
      "role": "system",
      "content": (
          "You are an HR assistant with access to the company's employee database "
          "through function calling. You must NEVER write code or describe function "
          "calls as text. Instead, use the native tool calling mechanism provided by "
          "the API. When a user asks about employee data, invoke the appropriate tool directly."
      )
  }
  ```
- Debugged by printing `response.choices[0].message.tool_calls` separately from `.content` to confirm whether a structured tool call was actually being emitted.

**Lesson:** When a model "talks about" calling a tool instead of calling it, check both the system prompt (does it clearly authorize/require tool use?) and the conversation history hygiene (are you re-injecting malformed prior turns?) before assuming it's a pure model-capability issue.

---

## Issue 5 — Invalid re-injected assistant message (`property 'annotations' is unsupported`)

**Symptom:**
```python
chat_history.append(response_message.model_dump())
```
```
groq.BadRequestError: 'messages.2' : for 'role:assistant' the following must be
satisfied[('messages.2' : property 'annotations' is unsupported)]
```

**Root cause:** `model_dump()` serializes the **entire** SDK response object, including internal/optional fields (`annotations`, etc.) that are valid in an API *response* but not accepted back in an API *request* payload. The response schema and the request schema are not identical.

**Fix:** Manually reconstruct the assistant message with only the fields the API accepts as input (`role`, `content`, `tool_calls`):
```python
assistant_message = {"role": "assistant", "content": response_message.content}
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
```

**Lesson:** Never blindly re-serialize an SDK response object back into a request payload. Response objects often carry extra metadata fields that break strict request-side validation. Reconstruct messages explicitly from the fields the API documents as valid input.

---

## Issue 6 — Deprecated model producing degraded tool-calling behavior

**Context:** Initial testing used `llama-3.1-8b-instant` and `llama-3.3-70b-versatile`. Groq announced (June 17, 2026) the deprecation of both models — recommended replacements are `openai/gpt-oss-20b` (for the 8B model) and `openai/gpt-oss-120b` or `qwen/qwen3.6-27b` (for the 70B model). Shutdown date: August 16, 2026 (models were still technically functional at time of testing, but flagged for migration).

**Fix:** Standardized on a single model for both the initial and follow-up API calls:
```python
MODEL = "openai/gpt-oss-120b"
```

**Lesson:** Groq's model lineup changes frequently; deprecated models may still respond but with degraded reliability for structured outputs like tool calls. When debugging erratic tool-calling behavior, checking the [Groq deprecations page](https://console.groq.com/docs/deprecations) is a useful early step, and it's worth keeping the model name in a single constant to avoid inconsistency between the "routing" call and the "final answer" call.

---

## Issue 7 — Model wrapping empty-parameter calls in bogus argument keys

**Symptom:**
```
DEBUG fn_args: {'': {}}
```
then, after a partial fix:
```
DEBUG fn_args: {'data': {}}
```
```
TypeError: get_all_employees() got an unexpected keyword argument '' / 'data'
```

**Root cause:** For a tool declared with no parameters (`"parameters": {"type": "object", "properties": {}}`), some models (observed with `openai/gpt-oss-120b`) generate a malformed arguments payload that wraps an empty object under an arbitrary or empty key, instead of emitting a clean `{}`. This is a model-generation quirk, not an application bug, and the exact wrapper key was not consistent across runs.

**Fix:** Rather than patching each observed variant individually, arguments are now validated against the tool's own declared schema — any key not present in `parameters.properties` is discarded, and if the schema declares no properties at all, the arguments are forced to `{}`:
```python
def clean_tool_args(fn_name: str, fn_args: dict, tools_schema: list) -> dict:
    schema = next(
        (t["function"]["parameters"] for t in tools_schema if t["function"]["name"] == fn_name),
        {}
    )
    expected_keys = set(schema.get("properties", {}).keys())
    if not expected_keys:
        return {}
    return {k: v for k, v in fn_args.items() if k in expected_keys}
```

**Lesson:** Don't trust generated tool arguments to exactly match the declared schema, even for zero-argument tools. Validate/sanitize `tool_call.function.arguments` against the tool's own `parameters.properties` before unpacking them into a Python function call — this covers unknown future variants of the same quirk, not just the ones observed so far.

---

## Issue 8 — Cascading failure on the follow-up API call (`tool_choice is none, but model called a tool`)

**Symptom:**
```
groq.BadRequestError: Tool choice is none, but model called a tool
```
appearing on the **second** (follow-up) completion call, which was made with `tool_choice="none"`.

**Root cause:** This was a *downstream consequence* of Issue 7, not an independent bug. Because the first tool execution failed (bad arguments → exception → error message sent back to the model), the model attempted to retry the same tool call on the next turn. Since the follow-up call explicitly disallows tool use (`tool_choice="none"`), the API rejected the model's retry attempt.

**Fix:** No separate fix needed — resolved automatically once Issue 7's argument-sanitization fix was applied, since the tool then succeeded on the first attempt and the model had no reason to retry.

**Lesson:** When two errors appear in sequence across two chained API calls, check whether the second is a *symptom* of the first before treating them as separate bugs. Fixing the root cause upstream can eliminate the downstream symptom entirely.

---

## Issue 9 — Generator closed prematurely (`Cannot operate on a closed database`)

**Symptom:**
```python
def get_all_employees(user_role=None):
    db = next(get_db())   # get_db() is a generator meant for FastAPI's Depends()
    try:
        return get_all_employees_logic(db)
    finally:
        db.close()
```
```
DEBUG ERROR: Cannot operate on a closed database.
```

**Root cause:** `get_db()` is a generator designed for FastAPI's `Depends()` mechanism, which holds a live reference to the generator for the duration of the request and only advances/closes it at the end. Calling `next(get_db())` outside of that context creates a generator object with **no persistent reference** anywhere except the local `next()` call. CPython's reference-counting garbage collector immediately collects the now-unreferenced generator, which triggers its `finally: conn.close()` block — closing the connection before `get_all_employees_logic()` ever runs.

**Fix:** Added a second, non-generator helper dedicated to direct (non-FastAPI) usage:
```python
# backend/database.py
def get_db():
    """Generator for FastAPI Depends()."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_db_connection() -> sqlite3.Connection:
    """Direct connection for non-FastAPI callers (e.g. the chatbot dispatcher)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```
Dispatcher updated accordingly:
```python
def get_all_employees(user_role=None):
    db = get_db_connection()   # no next(), already a live connection
    try:
        return get_all_employees_logic(db)
    finally:
        db.close()
```

**Lesson:** FastAPI-style `Depends()` generators are not safe to consume manually with `next()` outside of FastAPI's dependency-injection lifecycle — the lack of a persistent reference causes CPython to garbage-collect (and thus finalize/close) the generator almost immediately. Any code path that needs a DB connection outside of a FastAPI route should use a dedicated non-generator connection factory instead of repurposing the `Depends()` generator.

---

## Issue 10 — Wrong / inconsistent database path (`no such table: employees`)

**Symptom:**
```
DEBUG ERROR: no such table: employees
```
despite the connection succeeding.

**Root cause:** `DB_PATH` was defined as a relative path (`"hr_agent.db"`), which SQLite resolves relative to the **current working directory at launch time**, not relative to the location of `database.py` on disk. Since the FastAPI server and `chatbot.py` were launched from different working directories at different points during debugging, they were connecting to two different SQLite files — one containing the real schema/data, the other freshly created and empty (SQLite silently creates the file if it doesn't exist, which masks the misconfiguration instead of raising an error). The actual database file was also found to be named `app.db` and located inside `backend/`, not `hr_agent.db` at the project root as initially assumed.

**Fix:** Resolved the path relative to the source file itself, independent of the launch directory:
```python
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"  # backend/app.db, regardless of CWD
```

**Lesson:** Relative paths for persistent resources (databases, config files) are fragile across different entry points (server vs. CLI script vs. tests) that may be launched from different working directories. Anchor the path to `Path(__file__)` so it resolves consistently regardless of where the process was started from. Also: SQLite silently creating a missing file is a common source of "phantom empty database" bugs — always verify the actual file being connected to when data appears unexpectedly missing.

---

