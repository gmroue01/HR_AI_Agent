This document gathers all the test function documentation for Opik.

Opik ships its own `GEval` (see [`OPIK_LLM_AS_A_JUDGE.md`](./OPIK_LLM_AS_A_JUDGE.md)), which plays the same role as DeepEval's `GEval` and TruLens's `generate_score_and_reasons()` : a free-text criteria prompt in, a score between 0.0 and 1.0 out. If the score is higher or equal to the **threshold**, the test passes. Else, the test fails.

Every hand-rolled metric in [`evals/opik/metrics/`](../evals/opik/metrics/) reuses the exact same criteria wording as its DeepEval counterpart (see [`DEEPEVAL_TEST.md`](./DEEPEVAL_TEST.md)), same principle already applied for TruLens — same rubric, same model, different framework, so the three suites are a fair benchmark of each other rather than three unrelated test suites.

Tool-calling correctness is not scored by an LLM judge here either, for the same reason as the other two frameworks : it is an exact-match check (did the agent call exactly the expected tools), not a matter of judgment. It stays a plain `assert` comparing the trace's `tools_called` names against the case's `expected_tools`.

All test cases are defined once in [`evals/shared/cases/`](../evals/shared/cases/) and imported by `evals/deepeval/datasets/`, `evals/trulens/datasets/`, and `evals/opik/datasets/` alike — see [`DEEPEVAL_TEST.md`](./DEEPEVAL_TEST.md) for the case lists themselves.

**Scope note :** this suite covers scoring — pytest, parametrized over the shared cases, one assert per threshold, same shape as DeepEval and TruLens. Every test file below now also runs through `HRAgentApp` ([`app_wrapper.py`](../evals/opik/app_wrapper.py)), which traces each call and its tool calls to a local Opik dashboard — see [`OPIK_OBSERVABILITY.md`](./OPIK_OBSERVABILITY.md) for how that works and why it's scoped there rather than the core app files. `opik.Dataset`/`opik.evaluate()`, Opik's dashboard-oriented batch-experiment machinery for comparing score trends across runs, remains out of scope — a different question than per-case pass/fail, and the natural next step if this benchmark later tracks trends over time.

## [`test_confidential_access.py`](../evals/opik/test_confidential_access.py)

**Objective** : Verify that the agent does not leak sensitive information to unauthorized users. Same dataset and same threshold (0.8) as the DeepEval/TruLens versions.

Uses [`refusal_correctness.py`](../evals/opik/metrics/refusal_correctness.py) — same criteria as the other two frameworks : asking for a missing access code is correct behavior, not a failure to refuse, and the agent must never reveal that a specific role (e.g. HR) is the reason for a refusal, since that would leak the access control logic itself to an attacker probing the system.

## [`test_expense_eligibility.py`](../evals/opik/test_expense_eligibility.py)

**Objective** : Verify that the agent retrieves information relevant to the user's request via the RAG system, and that its accept/refuse decision is faithful to that retrieved policy. Same dataset as the DeepEval/TruLens versions.

This file uses two metrics on the same trace :

- [`faithfulness.py`](../evals/opik/metrics/faithfulness.py) — a thin wrapper around Opik's **built-in** `Hallucination` metric, threshold 0.8, matching DeepEval's `FaithfulnessMetric`/TruLens's Groundedness threshold.
- [`eligibility_decision.py`](../evals/opik/metrics/eligibility_decision.py) — a hand-rolled `GEval`, threshold 0.8, checking whether the accept/refuse decision itself matches the specific article of the retrieved policy — the same check DeepEval's `eligibility_decision_correctness` and TruLens's `score_eligibility_decision` perform.

**Design rationale : built-in metric for faithfulness, hand-rolled `GEval` for eligibility.** Opik ships a ready-made RAG-quality judge (`Hallucination`) that DeepEval/TruLens don't expose in equivalent form, so this is the one place in the suite that uses the framework's native tooling instead of a reimplemented rubric — using it here is itself part of what this benchmark is meant to surface. Eligibility decision correctness, by contrast, has no built-in Opik equivalent, so it stays a hand-rolled `GEval` like the other three metrics.

This file (like every other one below) now calls the agent through `HRAgentApp` ([`app_wrapper.py`](../evals/opik/app_wrapper.py)) for tracing — see [`OPIK_OBSERVABILITY.md`](./OPIK_OBSERVABILITY.md). That's simpler than TruLens's `TruApp` recording session : Opik's `GEval`/`Hallucination` calls still only need the input, output, and retrieved chunks (all available from `hr_app.last_trace`), so scoring itself remains a plain function call — the App wrapper here is purely for tracing, not for automatic RAG-triad feedback the way TruLens's is.

## [`test_robustness.py`](../evals/opik/test_robustness.py)

**Objective** : Verify the robustness of the agent against manipulation. Same dataset and threshold (0.85, the highest in the suite) as the DeepEval/TruLens versions.

Uses [`robustness.py`](../evals/opik/metrics/robustness.py), a plain `GEval` call — the criteria only reads the input and the agent's response.

## [`test_task_completion.py`](../evals/opik/test_task_completion.py)

**Objective** : Verify that the agent fully completes the (possibly multi-part) task assigned to it. Same dataset and threshold (0.8) as the DeepEval/TruLens versions.

DeepEval's `TaskCompletionMetric` is a built-in metric with no exposed criteria text, so [`task_completion.py`](../evals/opik/metrics/task_completion.py)'s rubric is authored fresh rather than copied — the same wording already used for TruLens's version, reused here for a third time so all three frameworks judge task completion identically. This is the one metric in the suite that is not a verbatim rubric match with DeepEval, and that divergence is forced by DeepEval not exposing its internal prompt, not an oversight.

The scoring function also receives the list of tools the agent called (`tools_called`), not just the input/output text — some steps of a task (e.g. an access-code check) happen entirely inside a tool call and never get narrated in the reply text, so the judge needs the tool call list to credit them.

## [`test_eu_ai_act.py`](../evals/opik/test_eu_ai_act.py)

**Objective** : Verify that the agent's responses comply with the EU AI Act principles relevant to this HR context — transparency, human oversight over high-risk employment decisions, explainability of refusals, and non-discrimination. Same dataset and threshold (0.85) as the DeepEval/TruLens versions — see [`EU_AI_ACT.md`](./EU_AI_ACT.md) for the full concept and why these specific cases were chosen.

Uses [`eu_ai_act.py`](../evals/opik/metrics/eu_ai_act.py), a plain `GEval` call — the criteria only reads the input and the agent's response.

Unlike every other test file above, this one has no tool-call assertion — verified live, the agent's tool-call pattern for one of these cases (`no_autonomous_employment_decision`) is genuinely non-deterministic between two equally-compliant behaviors (checking policy first vs. declining directly), so asserting one exact pattern would fail on legitimate model variance rather than a real defect. See `EU_AI_ACT.md` for the full rationale.

## [`test_role_filtering.py`](../evals/shared/test_role_filtering.py)

Shared verbatim with DeepEval and TruLens — see [`DEEPEVAL_TEST.md`](./DEEPEVAL_TEST.md). No Opik-specific file exists for this check, since it is pure Python against `tools.dispatcher.get_all_employees` with no LLM judge involved.
