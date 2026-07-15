# Frontend — Streamlit App

This document explains the Streamlit UI: how it manages state, how login and chat work, and what its current limitations are.

## Overview

The app has two screens, controlled by `st.session_state.user_role`:

- `user_role is None` → `show_login()` is displayed.
- `user_role is set` → `show_chat()` is displayed.

This check runs at the bottom of the script and acts as the app's router.

## How Streamlit state works here

Streamlit re-runs the entire script top to bottom on every user interaction (button click, form submit, chat input). `st.session_state` is the only mechanism that survives across these re-runs — it acts as per-session memory.

The script initializes four session values on first load:

- `user_role`: role of the logged-in employee, or `None`.
- `username`: display name shown in the chat header.
- `chat_history`: full conversation, starts as `[SYSTEM_PROMPT]`.
- `employee_id`: set on login, used to scope the agent's data access.

Without `session_state`, none of this would persist between interactions — every click would reset the app to a blank state.

## Login flow

`show_login()` renders a form (`surname`, `name`) and calls `login(surname, name)` on submit.

- If a matching employee is found: `user_role`, `username`, and `employee_id` are set, and `st.rerun()` forces the router to switch to `show_chat()`.
- If not: an error message is shown, state is left untouched.

## Chat flow

`show_chat()`:

1. Displays the logged-in user's name and role.
2. Renders every past `user`/`assistant` message from `chat_history` (the `system` message is never displayed).
3. On new input via `st.chat_input()`, calls `run_agent_turn(chat_history, user_input, user_role, employee_id=...)`, which returns the updated history and the assistant's reply.
4. Both are written to the screen and saved back to `session_state`.

The `Disconnect` button resets `user_role`, `username`, and `chat_history` to their initial state and re-runs the app.

## Security notes

**Authentication has no password.** `login()` currently authenticates on `surname` + `name` only. Anyone who knows an employee's name can log in as them and inherit their role and `employee_id`.

This has not been deliberately decided yet — it needs to be settled explicitly:
- If acceptable for now (e.g. closed internal prototype): note it here as an accepted risk, with a plan to add real authentication before any wider deployment.
- If not acceptable: add a password or another verification step before this app is used with real data.

Until this is decided, treat this as an open security issue, not a design choice.

