This document describes how access control is enforced in the HR agent, and why it is built the way it is.

**Access control** is the set of rules that decide who can see or change what. In this project, the running principle is : **authorization decisions are made in application code, never by the model**. The LLM can be asked to reason about a request, ask for missing verification, or explain a policy, but it never gets to decide, on its own judgment, whether a request is allowed. Every check below is a plain `if` statement in Python, not a prompt instruction the model could be talked out of.

## Identity is server-side, never model-supplied

`user_role` and `employee_id` come from the login step ([`auth.py`](../backend/auth.py)) and are stored in `st.session_state`. They are passed explicitly into [`run_agent_turn()`](../chatbot_core.py) as function parameters, and from there injected directly into every tool call :

```python
results = AVAILABLE_FUNCTIONS[fn_name](
    **fn_args, user_role=user_role, employee_id=employee_id)
```

The model is never asked for `user_role` or `employee_id`, and even if it tried to supply them anyway, [`clean_tool_args()`](../chatbot_core.py) filters every tool call's arguments down to only the keys declared in that tool's own JSON schema ([`tools/schemas.py`](../tools/schemas.py)) before the call is made — neither `user_role` nor `employee_id` is ever declared there, so a model-supplied value for either would be silently dropped even before the explicit keyword arguments above are applied.

**Design rationale** : this is what makes it safe to let the model call `submit_expense` or `update_my_wellness` freely — whichever employee the request is billed to or whose wellness gets updated is always the one who is actually logged in, never a value the conversation could talk the model into using.

## Field-level visibility

Which columns of an employee record are returned depends on `user_role` — see [`ROLE_BASED_AUTHORIZATION_SYSTEM.md`](./ROLE_BASED_AUTHORIZATION_SYSTEM.md) for the `FIELD_VISIBILITY` dictionary and `filter_field_by_role()`.

## The confidential-project gate

[`access_confidential_project()`](../tools/dispatcher.py) is a two-layer, ordered check :

```python
def access_confidential_project(project_code: str, query: str, user_role: str = None, employee_id: int = None):
    if user_role != "HR":
        return {"error": "Access denied."}

    if project_code != CONFIDENTIAL_PROJECTS_PASSWORD:
        return {"error": "Invalid password !!"}

    return search_confidential_projects_logic(query)
```

The role check runs **before** the code check, and is independent of it — a non-HR employee is denied even if they somehow have a valid code, and the two checks never get reordered or short-circuited based on anything the model does.

**Design rationale : why the role-denial error says "Access denied." and nothing more.** An earlier version of this message said *"Access restricted to HR personnel only"*. That leaks the access control logic itself : anyone probing the system — including a non-HR user who has no business knowing the gating rule exists — learns that becoming "HR" is the exact bypass condition to aim for. The agent always relays a tool's error message back to the user close to verbatim, so whatever the tool says becomes visible to whoever is asking. A generic denial reveals that access was refused, without revealing *why*, which is exactly what a request for confidential information from an unauthorized user should get.

## Server-side numeric limits

The 850 EUR monthly expense cap (`MOUTHLY_EXPENSE_LIMIT` in [`employee_service.py`](../backend/services/employee_service.py)) is checked in `submit_expense_logic()`, against the employee's actual stored `expense_amount` — not something the model computes or is trusted to enforce itself. The agent can be asked to explain the policy or the running total, but whether a submission is actually accepted is decided by this one comparison in code.
