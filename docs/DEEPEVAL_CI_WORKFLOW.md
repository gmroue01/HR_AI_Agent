# CI Workflow: LLM Agent Evaluation (DeepEval)

## Purpose

This GitHub Actions workflow (`.github/workflows/deepeval.yml`) automatically runs the full evaluation suite on every push or pull request targeting `main`, so that regressions in agent behavior — tool selection, refusal correctness, RAG faithfulness, task completion, robustness to manipulation — are caught before merging, rather than relying on manual re-testing.

## Trigger

```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
```

Runs on any push to `main`, and on any pull request targeting `main` — giving visibility into evaluation results both during PR review and after merge.

## Job breakdown

### 1. Environment setup

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
```

Checks out the repository and provisions a clean Python 3.11 environment. This runs on `ubuntu-latest` — a fresh container with nothing pre-installed, which is why every dependency and piece of state the tests need must be set up explicitly in the steps that follow (this is what originally surfaced several path- and environment-specific bugs that were invisible locally).

### 2. Dependency installation

```yaml
- name: Install dependencies
  run: |
    pip install -e .
    pip install deepeval
```

Installs the project itself in editable mode (making `backend`, `tools`, `rag` importable) plus DeepEval. Because CI starts from nothing, this step depends on `requirements.txt`/`pyproject.toml` being a minimal, accurate, cross-platform dependency list — not a raw `pip freeze` dump from a local Windows environment, which previously caused failures here (non-existent pinned versions, Windows-only packages).

### 3. Test database initialization

```yaml
- name: Initialize test database
  run: |
    python -c "from backend.init_db_sqlite3 import init_db; init_db()"
    python -c "
    from backend.database import get_db_connection
    db = get_db_connection()
    db.execute(\"INSERT INTO employees (surname, name, role, salary, wellness, expense_amount) VALUES ('Test', 'User', 'employee', 3000, 'healthy', 0)\")
    db.commit()
    db.close()
    "
```

Since CI has no pre-existing `app.db` (unlike a local dev machine with accumulated real data), this step creates the schema from scratch and seeds a single test employee record — required for any test that calls `get_all_employees`, `get_my_info`, or similar tools against `employee_id=1`.

### 4. Deterministic PII tests (blocking)

```yaml
- name: Run deterministic PII tests (blocking, zero tolerance)
  run: pytest evals/test_role_filtering.py -v
```

Runs plain pytest assertions — no LLM judge involved — that verify role-based field visibility (e.g. an `employee` role must never see `salary` or `wellness`). This step has no `continue-on-error`, meaning a failure here **fails the whole job**. This is intentional: PII leakage is a binary pass/fail concern, not something that should be softened by a threshold or treated as a warning.

### 5. LLM-as-judge evaluation suite (non-blocking)

```yaml
- name: Run LLM-as-judge evaluation suite (non-blocking, for visibility)
  continue-on-error: true
  env:
    GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
  run: |
    deepeval test run \
      evals/test_confidential_access.py \
      evals/test_expense_eligibility.py \
      evals/test_task_completion.py \
      evals/test_robustness.py
```

Runs the full DeepEval suite: tool correctness, refusal correctness, RAG faithfulness, eligibility decision correctness, task completion, and robustness to manipulation attempts. `GROQ_API_KEY` is injected from a repository secret, since the custom `GroqJudge` model used by these metrics needs it to call the Groq API.

**`continue-on-error: true`** deliberately makes this step non-blocking: LLM-as-judge scores carry inherent variance from run to run (the judge itself is a language model), so a borderline score here is treated as a signal to review rather than an automatic merge-blocker. Results remain fully visible in the CI logs regardless of pass/fail status.

## Design rationale: why some tests block and others don't

| Test category | Blocking? | Reasoning |
|---|---|---|
| PII / role-based field visibility | Yes | Deterministic, zero-tolerance — no LLM judgment involved, no acceptable margin of error |
| Tool correctness, refusal correctness, faithfulness, task completion, robustness | No (`continue-on-error`) | LLM-as-judge scoring has inherent variance; failures are meant to be reviewed, not treated as hard blockers by default |

This split can be revisited once score stability across multiple CI runs has been observed over time — if certain LLM-as-judge metrics prove consistently reliable, they could be promoted to blocking status.

## Prerequisites for this workflow to run correctly

- `.github/workflows/` must be spelled with the leading dot exactly — GitHub silently ignores workflow files placed anywhere else.
- `requirements.txt` / `pyproject.toml` must list only genuine, cross-platform, unpinned (or sensibly pinned) direct dependencies.
- The `GROQ_API_KEY` secret must be configured under repository **Settings → Secrets and variables → Actions**.
- `backend/init_db_sqlite3.py`'s `DB_PATH` must resolve correctly relative to its own file location, not the working directory the script happens to be invoked from.