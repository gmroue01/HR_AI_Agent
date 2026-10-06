This document describes the judge calibration mechanism in [`evals/shared/test_judge_calibration.py`](../evals/shared/test_judge_calibration.py). **The three example cases now have labels — but they were drafted by Claude (the assistant) reading real agent output against the real policy PDF, not by an independent human. The mechanism is fully validated end-to-end for real; the actual epistemic goal (an independent human perspective on the judge) is not yet met. Treat the current labels as a worked example to review or overwrite, not as trusted ground truth.**

## The problem this addresses

Every quality metric in this project — DeepEval, TruLens, Opik, Promptfoo, and the McNemar/permutation regression suites — is scored by the same single judge model: `GroqJudge` wrapping `openai/gpt-oss-120b` (see [`DEEPEVAL_LLM_AS_A_JUDGE.md`](./DEEPEVAL_LLM_AS_A_JUDGE.md)). Nothing in the project checks whether that judge's scores are actually *right* — whether they track a real notion of "correct" rather than some systematic bias of that one model (positional bias, self-preference, over- or under-leniency on a given criterion). Since every suite shares the same judge, a bias in it propagates silently to everything downstream, and nothing else in the benchmark would catch it — the four frameworks differ in scoring machinery, not in which model actually does the scoring.

The standard fix for this in LLM-eval practice is to compare a sample of judge scores against human-assigned scores on the same cases and measure agreement.

## What's implemented

[`evals/shared/cases/judge_calibration_labels.py`](../evals/shared/cases/judge_calibration_labels.py) holds a dict keyed by case name from [`expense_eligibility.py`](../evals/shared/cases/expense_eligibility.py), each entry a `{human_score, human_reason}` pair.

[`test_judge_calibration.py`](../evals/shared/test_judge_calibration.py) has two tests:

**1. `test_judge_score_agrees_with_human_label`** (parametrized over the three cases):
1. Looks up the case's label. If `human_score` is `None`, `pytest.skip()`s immediately — before running the agent or spending any Groq tokens.
2. Otherwise, runs the real agent turn, and — mirroring the same gap [`STATISTICAL_TEST.md`](./STATISTICAL_TEST.md)'s permutation test hit — skips if `search_hr_documents` wasn't called on this particular run, since without retrieved policy text there's no ground truth for either the judge or a human to score against.
3. Scores the reply with the same `eligibility_decision_correctness` GEval metric every other suite already uses.
4. Asserts `|human_score - judge_score| <= 0.2` (`AGREEMENT_TOLERANCE`), reporting both scores and both reasons on failure.

**2. `test_judge_human_agreement_kappa`** — a second, aggregate check across all labeled cases at once:
1. Collects one `(human_score, judge_score)` pair per labeled, scoreable case.
2. Converts each pair to booleans using the metric's own `threshold` (0.8) — `human_score >= 0.8` vs `judge_score >= 0.8` — since Cohen's kappa needs categorical labels, not continuous scores.
3. Computes Cohen's kappa directly (`cohen_kappa()`, a ~10-line implementation rather than pulling in scikit-learn/statsmodels for one formula):
   ```
   kappa = (p_o - p_e) / (1 - p_e)
   ```
   `p_o` is the observed agreement rate; `p_e` is the agreement expected by chance alone from each rater's own marginal pass rate — playing the same role `scipy.stats.binomtest`'s null hypothesis plays for McNemar's test elsewhere in this project, just for two raters instead of two conditions. Verified against known reference cases before use: perfect agreement → `1.0`, perfect disagreement → `-1.0`, degenerate all-same-label input → `None` (kappa is undefined, the same reasoning McNemar uses to skip on zero discordant pairs).
4. Skips if fewer than 2 labeled+scoreable cases exist, or if `kappa` comes back `None`.
5. Asserts `kappa >= 0.6` (`KAPPA_THRESHOLD`, "substantial agreement" on the Landis & Koch scale).

## How to actually calibrate the judge

Overwrite the labels in `judge_calibration_labels.py` by hand: read each case's `input` in [`expense_eligibility.py`](../evals/shared/cases/expense_eligibility.py) against `data/hr_policies/expense_policy.pdf`, decide what score you'd personally give the agent's real reply, and record it with a short reason.

## Real-run validation

Both tests were run for real. `test_judge_score_agrees_with_human_label` passed 2/3 or 1/3 depending on the run — `ineligible_parking_fine` flips between real runs: the agent has been observed both correctly refusing (citing Article 7 explicitly) and incorrectly approving (when top-3 retrieval missed Article 7 and the model misapplied an unrelated "parking fees" clause) for the *identical* input. `test_judge_human_agreement_kappa` ran end-to-end and returned **κ = 0.000** on one real run (pairs: `[(True, True), (True, True), (False, True)]`) — "no better than chance." That result was produced against the *original* `ineligible_parking_fine` label (`0.1`), which turned out to have been drafted from a single, apparently atypical run: across 4 observed real runs, 3 correctly refused (citing Article 7) and only 1 wrongly approved (a retrieval gap). The label has since been updated to `0.9` to reflect the more frequent, correct behavior — kappa has not yet been re-run against the corrected label.

## What's still open

- The three labels are AI-drafted examples, not real human judgment — the whole point of comparing against a human is a perspective genuinely independent of an LLM doing the judging, which an AI-drafted label doesn't provide.
- `ineligible_parking_fine`'s label may need revisiting: it was drawn from a run where RAG retrieval missed the relevant policy article, which later runs suggest is not the agent's typical behavior for this input.
- `AGREEMENT_TOLERANCE = 0.2` and `KAPPA_THRESHOLD = 0.6` are both starting points, not derived from any formal analysis.
- Only `expense_eligibility` cases are covered. `task_completion`, `confidential_access`, `eu_ai_act`, and `robustness` each use a different judge metric and would need their own labels and calibration tests.
- With only 3 cases, both `AGREEMENT_TOLERANCE` and kappa are on the small side of what either statistic is really meant for — kappa in particular is conventionally more meaningful past a couple dozen paired labels.
