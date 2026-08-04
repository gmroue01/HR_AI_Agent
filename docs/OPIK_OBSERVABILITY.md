This document describes Opik's tracing/observability layer as implemented in this project — the piece that differentiates Opik from DeepEval and TruLens in this benchmark. Opik Phase A ([`OPIK_TEST.md`](./OPIK_TEST.md)) covers scoring only; this is the tracing layer built on top of it.

**Observability**, in this context, means every agent call produces a **trace** — a record of what happened (input, output, timing) — with **spans** nested underneath it for each meaningful sub-step (here, each tool call), viewable in a dashboard rather than only returned in-process. `docs/TRACE_SYSTEM.md` already describes this project's own in-process `trace` dict returned by `run_agent_turn`; Opik's tracing is the same idea, pushed to a real backend with a UI instead of staying inside the Python process.

## Why this lives in `evals/opik/app_wrapper.py`, not `chatbot_core.py`

`chatbot_core.py` and `tools/dispatcher.py` have zero eval-framework imports today — this was a deliberate choice, matched exactly by TruLens's own `evals/trulens/app_wrapper.py`, which wraps `run_agent_turn` without touching the core files either. `evals/opik/app_wrapper.py`'s `HRAgentApp` class follows the same pattern : `@opik.track(name="run_agent_turn", type="general", project_name="HR_AgentIA")` sits on a `run()` method that calls `run_agent_turn` internally, so `opik` never becomes a hard dependency of the production agent.

**Trade-off, stated plainly** : this only traces calls made through `HRAgentApp` — every Opik test file uses it, so every Opik-suite run is traced, but a manual Streamlit session isn't, unless the app opts into the wrapper separately later.

`PROJECT_NAME = "HR_AgentIA"` is set explicitly on every span, kept distinct from the pre-existing `"Opik Demo Agent Observability"` project already present in the same local Opik install (a leftover from an unrelated earlier demo, matching `~/.opik.config`).

## How nested tool-call spans are created without touching `tools/dispatcher.py`

`run_agent_turn` already returns a `trace` dict with `tools_called: [{"name", "arguments", "result"}, ...]`, collected after each tool call completes (see `chatbot_core.py`). Inside `HRAgentApp.run()`, once the `@opik.track` decorator has opened the root span, `_log_tool_spans()` :

1. Calls `opik_context.get_current_span_data()` to get the currently-open root span's `trace_id` and `id`.
2. For each entry in `trace["tools_called"]`, creates a child span with `opik.Opik().span(trace_id=..., parent_span_id=..., name=call["name"], type="tool", input=..., output=...)`, then immediately calls `.end()` on it.

This reconstructs the tool-call spans **post-hoc**, from data the agent already collects, instead of instrumenting each tool function directly. Verified against the running local server via Opik's own REST API (`GET /api/v1/private/spans?trace_id=...`) : a real trace for the `eligible_taxi` case showed `span_count: 3` — the root `run_agent_turn` span (`type: general`) plus two child spans, `search_hr_documents` and `submit_expense` (both `type: tool`), each correctly `parent_span_id`-linked to the root, each carrying its real tool arguments and result as `input`/`output`. Cases where the agent doesn't call any tool correctly produce a trace with no child spans (`has_tool_spans: false`) — there's nothing to nest when nothing was called.

## Running the local Opik server

The self-hosted stack lives in a separate `comet-ml/opik` clone at `C:\Users\gmrou\opik` (outside this repo — it's Comet's own project, not part of `HR_AgentIA`), left over from an earlier, unrelated demo. To bring it up : start Docker Desktop, then from that directory run `.\opik.ps1`, which starts the full docker-compose stack (ClickHouse, MySQL, Redis, MinIO, ZooKeeper, the Opik backend, Python backend, and frontend) and prints the UI URL — `http://localhost:5173`, matching the pre-existing `~/.opik.config`.

## Viewing a trace

Open `http://localhost:5173`, select the `HR_AgentIA` project (workspace `default`), and open any trace from an Opik test run. The trace view shows the root `run_agent_turn` span with its full input/output, and the tool calls it made nested underneath as child spans — each with its own arguments and result, in the order they were called.

## Scope

Every Opik test file (`test_confidential_access.py`, `test_expense_eligibility.py`, `test_robustness.py`, `test_task_completion.py`, `test_eu_ai_act.py`) now goes through `HRAgentApp.run()` instead of calling `run_agent_turn` directly, so every one of them is traced — a broader scope than TruLens, which only wired its App wrapper into its one flagship RAG-triad test file, since Opik's tracing needs no extra `Feedback`/`Selector` machinery to apply everywhere.

No `opik.Dataset`/`opik.evaluate()` is used — that's Opik's batch-experiment machinery for comparing score trends across runs in the dashboard, a different question than "does this trace show the right spans," and remains out of scope for the same reason it was in Phase A : it's the natural next step if this benchmark later moves toward tracking trends across runs rather than pass/fail per commit.
