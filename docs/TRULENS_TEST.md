This document gathers all the test function documentation for TruLens.

TruLens has no `GEval`-equivalent by name. Instead, `generate_score_and_reasons()` (see [`TRULENS_LLM_AS_A_JUDGE.md`](./TRULENS_LLM_AS_A_JUDGE.md)) plays the same role : a free-text criteria prompt in, a score between 0.0 and 1.0 out. If the score is higher or equal to the **threshold**, the test passes. Else, the test fails.

Every custom metric in [`evals/trulens/metrics/`](../evals/trulens/metrics/) reuses the exact same criteria wording as its DeepEval counterpart (see [`DEEPEVAL_TEST.md`](./DEEPEVAL_TEST.md)), so both frameworks judge the same scenario against the same rubric — this is what makes the two suites a fair benchmark of each other rather than two unrelated test suites.

Tool-calling correctness is not scored by an LLM judge here either. Like DeepEval's `ToolCorrectnessMetric`, it is really an exact-match check (did the agent call exactly the expected tools) rather than a matter of judgment, so it stays a plain `assert` comparing the trace's `tools_called` names against the case's `expected_tools`.

All test cases are defined once in [`evals/shared/cases/`](../evals/shared/cases/) and imported by both `evals/deepeval/datasets/` and `evals/trulens/datasets/` — see [`DEEPEVAL_TEST.md`](./DEEPEVAL_TEST.md) for the case lists themselves.

## [`test_confidential_access.py`](../evals/trulens/test_confidential_access.py)

**Objective** : Verify that the agent does not leak sensitive information to unauthorized users. Same dataset and same threshold (0.8) as the DeepEval version.

Uses [`refusal_correctness.py`](../evals/trulens/metrics/refusal_correctness.py) — the criteria explicitly states that asking for the missing access code is correct behavior, not a failure to refuse, and that the agent must never reveal that a specific role (e.g. HR) is the reason for a refusal, since that would leak the access control logic itself to an attacker probing the system.

## [`test_expense_eligibility.py`](../evals/trulens/test_expense_eligibility.py)

**Objective** : Verify that the agent retrieves information relevant to the user's request via the RAG system, and that its accept/refuse decision is faithful to that retrieved policy. Same dataset as the DeepEval version.

This is the one file that uses TruLens's full instrumentation idiom — `HRAgentApp` (an `@instrument`-decorated wrapper around `run_agent_turn`, see [`app_wrapper.py`](../evals/trulens/app_wrapper.py)), a `TruApp` recorder, and the three RAG Triad feedbacks from [`feedback_functions.py`](../evals/trulens/feedback_functions.py) :

- **Context Relevance** — is the retrieved chunk actually relevant to the question ?
- **Groundedness** — is the answer supported by the retrieved chunk, or does it hallucinate beyond it ?
- **Answer Relevance** — does the answer actually address the question asked ?

Together these three are the **RAG Triad**, the benchmark dimension named in `goals.md` ("Rag system (hallucination, rag triad)"). Each is thresholded at 0.8, matching DeepEval's `FaithfulnessMetric` threshold.

A single `hr_app.run(...)` call inside `with tru_recorder as recording:` executes the agent once; `record.retrieve_feedback_results()` then blocks until TruLens's feedback evaluators (which run as background threads) finish, returning a one-row `DataFrame` with a score per feedback name.

The tool-name assert and the `retrieval_context` (both needed for the eligibility-decision check below) are read from `hr_app.last_trace`, stashed by `app_wrapper.py` during that same single call — no second agent invocation is made.

On top of the RAG Triad, [`eligibility_decision.py`](../evals/trulens/metrics/eligibility_decision.py) checks whether the accept/refuse decision itself matches the specific article of the retrieved policy (threshold 0.8) — the same check DeepEval's `eligibility_decision_correctness` GEval performs, called here as a plain function since it needs no TruLens-specific recording (it only needs the input, output, and retrieved chunks, all already available from the trace).

**Design rationale** : the full `TruApp`/`Feedback`/`Selector` machinery is used here and nowhere else in this suite, because this is the one place where TruLens's automatic, selector-driven scoring is actually the point — TruLens's flagship pattern is the RAG Triad. Every other test file below calls `generate_score_and_reasons()` directly, since a single free-standing criteria check on input/output (plus, where needed, the trace) does not need an app recording session.

## [`test_robustness.py`](../evals/trulens/test_robustness.py)

**Objective** : Verify the robustness of the agent against manipulation. Same dataset and threshold (0.85, the highest in the suite, since these cases are highly sensitive) as the DeepEval version.

Uses [`robustness.py`](../evals/trulens/metrics/robustness.py), a plain call to `generate_score_and_reasons()` — no recording needed, since the criteria only reads the input and the agent's response.

## [`test_task_completion.py`](../evals/trulens/test_task_completion.py)

**Objective** : Verify that the agent fully completes the (possibly multi-part) task assigned to it. Same dataset and threshold (0.8) as the DeepEval version.

DeepEval's `TaskCompletionMetric` is a built-in metric with no exposed criteria text, so [`task_completion.py`](../evals/trulens/metrics/task_completion.py)'s rubric is authored fresh rather than copied — this is the one metric in the suite that is not a verbatim rubric match with its DeepEval counterpart, and that divergence is forced by DeepEval not exposing its internal prompt, not an oversight.

The scoring function also receives the list of tools the agent called (`tools_called`), not just the input/output text — some steps of a task (e.g. an access-code check) happen entirely inside a tool call and never get narrated in the reply text, so the judge needs the tool call list to credit them.

## [`test_role_filtering.py`](../evals/shared/test_role_filtering.py)

Shared verbatim with DeepEval — see [`DEEPEVAL_TEST.md`](./DEEPEVAL_TEST.md). No TruLens-specific file exists for this check, since it is pure Python against `tools.dispatcher.get_all_employees` with no LLM judge involved.

## [`run_single_test.py`](../evals/trulens/run_single_test.py)

Not part of the pytest suite above — this is a manual smoke-test script, run directly with `python -m evals.trulens.run_single_test`. It fires a single hardcoded case through `HRAgentApp` inside a `TruApp` recording and prints the RAG Triad scores once `record.retrieve_feedback_results()` returns, instead of asserting against a threshold.

Its purpose is quick manual sanity-checking while iterating on [`feedback_functions.py`](../evals/trulens/feedback_functions.py) or [`app_wrapper.py`](../evals/trulens/app_wrapper.py) — seeing raw scores for one case is faster than running the full parametrized suite, which calls the live agent and judge multiple times.
