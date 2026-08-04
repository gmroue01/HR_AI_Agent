# CI Workflow: LLM Agent Evaluation (Opik)

## Purpose

This GitHub Actions workflow (`.github/workflows/opik.yml`) automatically runs the Opik evaluation suite on every push or pull request targeting `main`, mirroring [`DEEPEVAL_CI_WORKFLOW.md`](./DEEPEVAL_CI_WORKFLOW.md)'s and [`TRULENS_CI_WORKFLOW.md`](./TRULENS_CI_WORKFLOW.md)'s pipeline so all three frameworks are exercised the same way on every change.

## Trigger

```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
```

Same trigger as the other two workflows — on any push to `main`, and on any pull request targeting `main`.

## Job breakdown

### 1. Environment setup, 2. Dependency installation, 3. Test database initialization

Identical in spirit to [`DEEPEVAL_CI_WORKFLOW.md`](./DEEPEVAL_CI_WORKFLOW.md)'s steps 1–3 — same Python 3.11 setup on a clean `ubuntu-latest` container, same DB init script. The only difference is the dependency install step, which installs `opik` and `litellm` instead of `deepeval` or `trulens` :

```yaml
- name: Install dependencies
  run: |
    pip install -e .
    pip install opik litellm
```

### 4. Deterministic PII tests (blocking)

```yaml
- name: Run deterministic PII tests (blocking, zero tolerance)
  run: pytest evals/shared/test_role_filtering.py -v
```

Runs the exact same file as the DeepEval and TruLens workflows' equivalent step — `evals/shared/test_role_filtering.py` has no framework-specific code, so there is one shared PII check, not three copies that could drift apart.

### 5. LLM-as-judge evaluation suite (non-blocking)

```yaml
- name: Run LLM-as-judge evaluation suite (non-blocking, for visibility)
  continue-on-error: true
  env:
    GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
  run: |
    pytest \
      evals/opik/test_confidential_access.py \
      evals/opik/test_expense_eligibility.py \
      evals/opik/test_task_completion.py \
      evals/opik/test_robustness.py \
      -v
```

Like TruLens, Opik has no `deepeval test run`-style CLI wrapper, so plain `pytest` is the natural fit. `GROQ_API_KEY` is required for the same reason as the other two workflows : [`judge_model.py`](../evals/opik/judge_model.py)'s `GroqLiteLLMChatModel` calls Groq through LiteLLM's `groq/` prefix, and the agent itself is Groq-hosted too.

`continue-on-error: true` is set for the same reason as the other two workflows' non-blocking step — LLM-as-judge scores carry inherent variance from run to run, so a borderline score here is a signal to review, not a merge-blocker.

This step needs no local Opik server to run correctly : the metrics used here (`GEval`, `Hallucination`) call Groq directly through LiteLLM, independent of whether Opik's own tracing backend is reachable. A local server is only needed for the tracing/dashboard layer, which this suite does not use yet (see [`OPIK_TEST.md`](./OPIK_TEST.md)'s scope note).

## Design rationale: why some tests block and others don't

| Test category | Blocking? | Reasoning |
|---|---|---|
| PII / role-based field visibility (`evals/shared/test_role_filtering.py`) | Yes | Deterministic, zero-tolerance — no LLM judgment involved, no acceptable margin of error |
| Refusal correctness, faithfulness, eligibility decision, task completion, robustness | No (`continue-on-error`) | LLM-as-judge scoring has inherent variance; failures are meant to be reviewed, not treated as hard blockers by default |

Same split, same reasoning, as [`DEEPEVAL_CI_WORKFLOW.md`](./DEEPEVAL_CI_WORKFLOW.md) and [`TRULENS_CI_WORKFLOW.md`](./TRULENS_CI_WORKFLOW.md) — this is a property of testing a live LLM agent with an LLM judge, not of any one framework.

## Prerequisites for this workflow to run correctly

- `.github/workflows/` must be spelled with the leading dot exactly.
- `opik` and `litellm` must be declared in `pyproject.toml`'s `opik` optional-dependencies group (they were previously only present in the local dev venv, not declared anywhere — a fresh CI checkout would otherwise fail to install them).
- The `GROQ_API_KEY` secret must be configured under repository **Settings → Secrets and variables → Actions** (the same secret the other two workflows use).
- `backend/init_db_sqlite3.py`'s `DB_PATH` must resolve correctly relative to its own file location, not the working directory the script happens to be invoked from.
