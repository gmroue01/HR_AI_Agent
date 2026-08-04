This document describes the `LLM-as-a-judge` logic implemented in this project for Opik.

The logic is defined in [`judge_model.py`](../evals/opik/judge_model.py).

The model used as `LLM-as-a-judge` is the same as DeepEval's and TruLens's : **`openai/gpt-oss-120b`**, called through Groq.

## `judge_model` object

Like TruLens, Opik does not require writing a custom class from scratch — `LiteLLMChatModel` (from `opik.evaluation.models`) is a ready-made model wrapper that can call any model LiteLLM supports. `judge_model` is a small subclass of it, instantiated once and pointed at Groq's `openai/gpt-oss-120b` through LiteLLM's `groq/` model-name prefix :

```python
class GroqLiteLLMChatModel(LiteLLMChatModel):
    @property
    def supported_params(self):
        return LiteLLMChatModel.supported_params.func(self) - {"logprobs", "top_logprobs"}

judge_model = GroqLiteLLMChatModel(model_name="groq/openai/gpt-oss-120b")
```

**Why the subclass, and not just `LiteLLMChatModel(model_name=...)` directly ?** Opik's `GEval` metric turns on `logprobs`/`top_logprobs` in its scoring request whenever the model's `supported_params` reports both as available, in order to compute a confidence-weighted score. LiteLLM's static capability table reports Groq as supporting them — but Groq's API actually rejects `logprobs` for this specific model (`` `logprobs` is not supported with this model ``). The subclass strips those two names out of `supported_params` before `GEval` ever reads it, so it falls back to its plain (non-logprobs-weighted) scoring path instead of failing outright.

## `GEval` — the GEval-equivalent primitive

Opik ships its own `GEval` class (`opik.evaluation.metrics.GEval`), doing the same job as DeepEval's `GEval` (see [`DEEPEVAL_LLM_AS_A_JUDGE.md`](./DEEPEVAL_LLM_AS_A_JUDGE.md)) and TruLens's `generate_score_and_reasons()` (see [`TRULENS_LLM_AS_A_JUDGE.md`](./TRULENS_LLM_AS_A_JUDGE.md)) : give it a free-text rubric, it returns a score plus a reason.

The construction shape is close to DeepEval's :

```python
GEval(
    task_introduction="...",
    evaluation_criteria="...",
    model=judge_model,
)
```

**The one real difference : `.score()` takes a single string.** DeepEval's `GEval` is called with a full `LLMTestCase` (input, actual output, retrieval context, ... as separate fields) every time. Opik's `GEval.score(output: str, **ignored_kwargs)` only accepts one `output` string — `task_introduction`/`evaluation_criteria` are fixed once, at construction time, not passed per call. Every metric in [`evals/opik/metrics/`](../evals/opik/metrics/) therefore folds whatever it needs (input, retrieved context, tools called, the agent's reply) into one formatted block before calling `.score()`.

**Score scale.** Opik's `GEval` expects the judge to answer with an integer score from 0 to 10, then divides by 10 to normalize to 0.0–1.0 — this is baked into its response schema and its chain-of-thought generation step, not something the caller configures. The `evaluation_criteria` strings in this project describe the rubric only, with no scale instructions of their own, so there is nothing to conflict with Opik's own scale handling.

## `Hallucination` — a built-in RAG-quality judge

For the faithfulness dimension, [`faithfulness.py`](../evals/opik/metrics/faithfulness.py) uses Opik's built-in `Hallucination` metric (`opik.evaluation.metrics.Hallucination`) instead of a hand-rolled `GEval`. It takes `input`, `output`, and `context` directly, so no output-string folding is needed for this one.

**Score polarity is inverted compared to everything else in this benchmark.** `Hallucination.score(...)` returns `1.0` when hallucination **is** detected and `0.0` when the output is faithful — the opposite of DeepEval's `FaithfulnessMetric` and TruLens's Groundedness, which both score higher = more faithful. `score_faithfulness()` inverts it (`1.0 - result.value`) before comparing against the threshold, so `THRESHOLD = 0.8` keeps the same "higher is better" meaning used everywhere else in this project.

## Why is there no `GroqJudge`-equivalent class ?

Same reason as TruLens : DeepEval requires subclassing `DeepEvalBaseLLM` because it needs a judge object matching a specific interface. Opik's `LiteLLMChatModel` already speaks LiteLLM's model interface directly, so the only code needed on top of it is the small `supported_params` override above — there is no equivalent full judge class to write.
