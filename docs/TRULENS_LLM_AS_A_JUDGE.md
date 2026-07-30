This document describes the `LLM-as-a-judge` logic, which is implemented in this project for TruLens.

The logic is defined in [`litellm_provider.py`](../evals/trulens/litellm_provider.py).

The model used as `LLM-as-a-judge` is the same as DeepEval's : **`openai/gpt-oss-120b`**, called through Groq.

## `provider` object.

Unlike DeepEval, TruLens does not require writing a custom class. `LiteLLM` (from `trulens.providers.litellm`) is a ready-made provider, already able to call any model LiteLLM supports. It is instantiated once, pointed at Groq's `openai/gpt-oss-120b` through LiteLLM's `groq/` model-name prefix :

```python
provider = LiteLLM(model_engine="groq/openai/gpt-oss-120b")
```

The `provider` object exposes two kinds of methods :

- **Built-in feedback functions**, e.g. `context_relevance_with_cot_reasons()`, `groundedness_measure_with_cot_reasons()`, `relevance_with_cot_reasons()` — the three legs of the RAG Triad (see [`TRULENS_TEST.md`](./TRULENS_TEST.md)).
- **`generate_score_and_reasons(system_prompt, ...)`** — a generic, free-text-criteria primitive. This is TruLens's equivalent of DeepEval's `GEval` (see [`DEEPEVAL_LLM_AS_A_JUDGE.md`](./DEEPEVAL_LLM_AS_A_JUDGE.md)) : give it a criteria prompt, it returns a score normalized to 0.0–1.0 plus a `reason`. Every custom metric in [`evals/trulens/metrics/`](../evals/trulens/metrics/) is built on top of this one method.

## Why is there no `GroqJudge`-equivalent class ?

DeepEval requires subclassing `DeepEvalBaseLLM`, because it needs a judge object matching a specific interface (`generate`/`a_generate`/`load_model`/`get_model_name`). TruLens's `LLMProvider` classes already ship with a rich set of feedback methods (relevance, groundedness, tone, etc.) plus the generic `generate_score_and_reasons` primitive, so there is no equivalent class to write for this project — `provider` from `litellm_provider.py` is used directly everywhere a judge is needed.
