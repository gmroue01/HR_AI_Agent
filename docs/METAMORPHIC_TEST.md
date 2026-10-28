This document gathers the test function documentation for the metamorphic-testing suite in [`evals/shared/test_metamorphic_expense_eligibility.py`](../evals/shared/test_metamorphic_expense_eligibility.py).

Every other suite in this project checks a single output against a fixed reference : a threshold score from an LLM-as-a-judge (DeepEval/TruLens/Opik), a canned mock (see [`MOCKING_TEST.md`](./MOCKING_TEST.md)), or a rendered UI state (see [`PLAYWRIGHT_TEST.md`](./PLAYWRIGHT_TEST.md)). Metamorphic testing checks something different : not whether one output is correct, but whether two related outputs are *consistent* with each other. A **metamorphic relation** defines a transformation of the input that should leave some property of the output unchanged — here, rewording a request without changing its meaning should not change which tools the agent decides to call. This sidesteps the usual LLM-testing problem of not having a ground-truth oracle for "the" correct answer : the test never asks whether the original response was right, only whether the reworded one agrees with it.

**Why tool calls, not the reply text.** As [`OPIK_TEST.md`](./OPIK_TEST.md) already notes for the other suites, tool-calling is exact-match, not a judgment call — the agent either called `submit_expense` or it didn't. For the expense eligibility cases in [`evals/shared/cases/expense_eligibility.py`](../evals/shared/cases/expense_eligibility.py), whether `submit_expense` appears in `trace["tools_called"]` *is* the accept/refuse decision (an accepted case's `expected_tools` includes it, a refused case's doesn't — see [`DEEPEVAL_TEST.md`](./DEEPEVAL_TEST.md)). That makes the set of tool names a decision proxy that can be compared with a plain `assert`, without adding another LLM judge call just to classify the reply text as "accepted" or "refused".

The paraphrases live in their own file, [`evals/shared/cases/expense_eligibility_paraphrases.py`](../evals/shared/cases/expense_eligibility_paraphrases.py) — a dict keyed by case name rather than an extra key merged into `expense_eligibility.py`, so the file every other framework already imports stays untouched. Each paraphrase is hand-written to preserve the original amount, expense type, and context while changing the sentence structure and wording, e.g. `"I'd like to submit a 45 EUR taxi expense for a late-night client meeting"` becomes `"Could you help me file an expense claim? I took a taxi home after a client meeting that ran late, it cost me 45 euros."`.

Both the original and the paraphrased input go through the real `chatbot_core.run_agent_turn()` — this can't be mocked away like [`MOCKING_TEST.md`](./MOCKING_TEST.md)'s suite, since the entire point is to check whether the real model stays consistent under rewording. Each test case therefore makes two real Groq calls.

## [`test_metamorphic_expense_eligibility.py`](../evals/shared/test_metamorphic_expense_eligibility.py)

**Objective** : Verify that rewording an expense request without changing its meaning does not change which tools the agent calls, for every case in `EXPENSE_ELIGIBILITY_CASES`.

- **`test_paraphrase_does_not_change_the_tools_called`** — parametrized over `eligible_taxi`, `ineligible_spa`, and `ineligible_parking_fine`. Runs `run_agent_turn()` once with the case's original `input` and once with its paraphrase from `EXPENSE_ELIGIBILITY_PARAPHRASES`, and asserts the two runs produce the same set of tool names.

Run with `pytest evals/shared/test_metamorphic_expense_eligibility.py -v`.

## Real run

```
evals/shared/test_metamorphic_expense_eligibility.py::test_paraphrase_does_not_change_the_tools_called[eligible_taxi] PASSED
evals/shared/test_metamorphic_expense_eligibility.py::test_paraphrase_does_not_change_the_tools_called[ineligible_spa] PASSED
evals/shared/test_metamorphic_expense_eligibility.py::test_paraphrase_does_not_change_the_tools_called[ineligible_parking_fine] PASSED

3 passed in 50.28s
```

All 3 cases passed on a single run, 6 real Groq calls (2 per case), no rate-limiting. For `eligible_taxi`, the original input (*"I'd like to submit a 45 EUR taxi expense for a late-night client meeting"*) and its paraphrase (*"Could you help me file an expense claim? I took a taxi home after a client meeting that ran late, it cost me 45 euros."*) produced the same tool set, and likewise for the two refusal cases — confirming the model's tool-choice behavior doesn't depend on the exact wording of the request.
