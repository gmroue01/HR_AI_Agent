**Status: partially implemented.** The core mechanism — [`evals/shared/regression_experiment.py`](../evals/shared/regression_experiment.py) — is real, runnable, and validated against the local Opik server. Running it on a recurring *schedule* is not: that piece is deliberately deferred, see [What's still open](#whats-still-open).

## The problem

Every regression signal in this project before this document (see [`TESTING_OVERVIEW.md`](./TESTING_OVERVIEW.md)) is triggered by a code change: the CI workflows (`.github/workflows/*.yml`) run `on: push` / `on: pull_request`, and the metamorphic/McNemar/AgentEvals suites compare two conditions *within the same run* (original vs. paraphrase, actual vs. reference trajectory).

None of that catches drift that has nothing to do with a code change. `chatbot_core.py` can sit untouched for weeks while the actual behavior of `openai/gpt-oss-120b` on Groq shifts underneath it — a silent model update on the provider's side, or just the accumulated effect of sampling variance never being watched over time. When the code is frozen and the behavior still changes, a code-diff-triggered CI run is structurally the wrong tool: there's no diff to react to. The only observable signal left is the model's own output, watched over time rather than compared once.

## Why a custom cron + JSON baseline isn't the best fit here

The straightforward fix is a scheduled job that reruns the same fixed cases regardless of code changes, diffing current scores against a stored baseline. That works, but it means building and maintaining, from scratch, exactly the machinery a dedicated eval platform already ships: experiment storage, historical comparison, a UI to view trends. This project already runs a self-hosted Opik instance for tracing (see [`OPIK_OBSERVABILITY.md`](./OPIK_OBSERVABILITY.md)), which — per that document's own scope note — deliberately left this piece out:

> No `opik.Dataset`/`opik.evaluate()` is used — that's Opik's batch-experiment machinery for comparing score trends across runs in the dashboard [...] the natural next step if this benchmark later moves toward tracking trends across runs rather than pass/fail per commit.

## What's implemented: `regression_experiment.py`

`evals/shared/cases/expense_eligibility.py` (the same case bank `TESTING_OVERVIEW.md` shows every framework re-exporting) is loaded into an `opik.Dataset` named `expense_eligibility_regression`, and scored with the exact same `GEval` instance `evals/opik/metrics/eligibility_decision.py`'s pytest suite already uses (exported as a public `metric` alias so both consumers share one judge/criteria definition instead of two copies that could drift apart).

- **`_build_dataset_items()`** builds `{name, input, user_role}` dicts from the case bank and `dataset.insert()`s them. Confirmed via Opik's REST API (`GET /api/v1/private/datasets?name=...`) that repeated inserts of the same case bank don't accumulate duplicates — Opik dedupes by content hash, so running this daily against an unchanged case bank stays at `dataset_items_count: 3`.
- **`task()`** runs the real `chatbot_core.run_agent_turn()` (same production entry point every other suite uses) and builds the same combined `"Retrieved policy context / User input / Agent response"` string the pytest version builds by hand, returned as `{"output": ...}` so Opik's automatic task-output-to-scoring-kwargs mapping feeds it straight into the metric.
- **`run_regression_experiment()`** calls `opik.evaluate(dataset=..., task=..., scoring_metrics=[metric], experiment_name=f"expense_eligibility-{date}", task_threads=1)`. Each run becomes a named **Experiment** attached to the dataset; Opik's dashboard renders score trends across experiments on the same dataset natively.

**`task_threads=1` is load-bearing, not a style choice.** The default (`task_threads=16`) fires every item's agent-turn call and judge call concurrently, which blew straight through Groq's 8000-tokens-per-minute cap even for 3 items during testing — the same reasoning as `workers: 1` in `playwright.config.ts` for the same underlying single-consumer Groq account.

**Real-run validation.** Run directly (`python -m evals.shared.regression_experiment`) against the local Opik server: dataset creation and item dedup confirmed via direct API call; at least one full run produced a real score (`Eligibility Decision Correctness: 0.5000`) uploaded to the dashboard. Getting a clean 3/3-scored run repeatedly was blocked by Groq's per-minute rate limit during testing — a symptom of how much of the daily/per-minute budget the rest of this project's suites were already consuming that session, not a defect in the script itself.

## What's still open

- **No scheduler.** The script is a manually-invoked tool (`python -m evals.shared.regression_experiment`), not yet wired to `on: schedule` in a GitHub Actions workflow. The blocker: the Opik server it talks to runs locally (`http://localhost:5173`, per `OPIK_OBSERVABILITY.md`), which a GitHub-hosted runner cannot reach. Wiring up a cron workflow needs one of: switching to Comet's cloud-hosted Opik (an account + API key), or exposing the local server through a tunnel (fragile — depends on the host machine being on). Deliberately deferred rather than building a workflow file that can't actually run.
- **Automation rules for continuous, non-batch monitoring** — Opik's server-side "online evaluation" rules (the TypeScript SDK's bundled types expose `AutomationRuleEvaluatorsClient` / `AutomationRuleEvaluatorPublic`), which would score every new trace automatically rather than only scheduled reruns of the fixed case bank — remain unexplored. The exact REST path wasn't confirmed against the local server (404 on the guessed paths).
- No threshold or "promotion" policy has been designed for deciding when a score drop across experiments is real drift versus normal judge variance (the same variance problem the McNemar/permutation suites already grapple with for a different comparison).
- Only `expense_eligibility` is covered — the other four case banks (`task_completion`, `confidential_access`, `eu_ai_act`, `robustness`) would each need their own `task()`/metric wiring the same way.
