# HR Agent — LLM Evaluation Benchmark

A small HR assistant chatbot (RAG + tool calling, built on Groq) used as a concrete test bed to benchmark four LLM evaluation frameworks — **DeepEval**, **TruLens**, **Opik**, and **Promptfoo** — plus a layer of statistical regression tests (McNemar, permutation, pass@k, metamorphic) and functional E2E tests (Playwright, Selenium).

The chatbot itself is a means to an end: the real deliverable is the documentation in [`docs/`](./docs), which explains how each framework is wired up, how they compare, and how to test an LLM agent beyond a single hardcoded assertion.

See [`goals.md`](./goals.md) for the project's motivation and scope.

## What the agent does

An HR chatbot with role-based access (employee / HR), backed by:

- **Function calling** against an employee SQLite database (own profile, wellness status, salary grid, expense submission).
- **RAG** over HR policy documents and the salary grid, via ChromaDB (`search_hr_documents`).
- **Confidential project access**, gated behind HR role + a server-validated access code (`access_confidential_project`).

Every capability is described in detail in [`docs/FEATURES.md`](./docs/FEATURES.md). The security model — why identity-bound values (like `employee_id`) are injected server-side and never trusted from the model — is in [`docs/ACCESS_CONTROL.md`](./docs/ACCESS_CONTROL.md) and [`docs/ROLE_BASED_AUTHORIZATION_SYSTEM.md`](./docs/ROLE_BASED_AUTHORIZATION_SYSTEM.md).

The single production entry point everything else in this repo tests is `chatbot_core.run_agent_turn()`.

## Project structure

```
chatbot_core.py       Agent orchestration loop (tool calling, retries) — the function under test everywhere
streamlit_app.py       Streamlit UI (login + chat)
backend/                FastAPI app, SQLite models, auth, employee/document services
rag/                     ChromaDB ingestion and retrieval
tools/                   Tool schemas exposed to the model + the dispatcher that executes them
data/                    HR policy docs, salary grid, confidential project files (source data for RAG)

tests/                   Unit tests — chatbot_core with a mocked Groq client
evals/
  shared/                Single source of truth: test cases + regression suites (McNemar, permutation,
                          pass@k, metamorphic, judge calibration) reused by every framework below
  deepeval/ trulens/ opik/ promptfoo/
                          Same test cases, run through each framework's own quality/judge metrics
  agentevals/            Tool-call trajectory tests
e2e/                     Playwright E2E tests (+ an LLM-judge test on real UI output)
e2e_selenium/            Selenium E2E tests (+ an LLM-judge test on real UI output)

docs/                    The actual deliverable — one .md per concept/framework/test type
```

[`docs/TESTING_OVERVIEW.md`](./docs/TESTING_OVERVIEW.md) is the map of how every test suite connects — read it first if you're new to the repo.

## Setup

Requires Python 3.10+ and a Groq API key.

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file at the project root:

```
GROQ_API_KEY=your_key_here
```

Initialize the database and ingest the RAG documents:

```bash
python backend/init_db_sqlite3.py
python -c "from rag.ingest import ingest_documents; ingest_documents(['data/hr_policies', 'data/salary_grids'])"
python -c "from rag.ingest import ingest_confidential_projects; ingest_confidential_projects('data/secret_projects')"
```

## Running the app

```bash
streamlit run streamlit_app.py
```

## Running the tests

```bash
# Unit tests (mocked LLM, no API calls)
pytest tests/

# Quality benchmark, one framework at a time
pytest evals/deepeval/
pytest evals/trulens/
pytest evals/opik/
npx promptfoo eval -c evals/promptfoo/promptfooconfig.yaml

# Regression / statistical suites (shared across frameworks)
pytest evals/shared/

# E2E
npx playwright test          # e2e/
pytest e2e_selenium/
```

Most `evals/` tests make real Groq API calls and are subject to Groq's shared rate limits (see [`docs/REGRESSION_MONITORING.md`](./docs/REGRESSION_MONITORING.md)); `pytest` is configured to auto-retry on `RateLimitError` (see `pyproject.toml`).

## Documentation

Everything beyond this quick start lives in [`docs/`](./docs), organized by concept:

- **Architecture & features**: `ARCHITECTURE/`, `FEATURES.md`, `RAG_SYSTEM.md`, `TRACE_SYSTEM.md`, `ACCESS_CONTROL.md`, `ROLE_BASED_AUTHORIZATION_SYSTEM.md`
- **Testing map**: `TESTING_OVERVIEW.md`
- **Per-framework**: `DEEPEVAL_*.md`, `TRULENS_*.md`, `OPIK_*.md`
- **Statistical / regression testing**: `STATISTICAL_TEST.md`, `METAMORPHIC_TEST.md`, `JUDGE_CALIBRATION.md`, `EVALUATION_METRICS.md`
- **E2E**: `PLAYWRIGHT_TEST.md`, `SELENIUM_TEST.md`
- **Compliance**: `EU_AI_ACT.md`
- **CI**: `DEEPEVAL_CI_WORKFLOW.md`, `OPIK_CI_WORKFLOW.md`, `TRULENS_CI_WORKFLOW.md`
