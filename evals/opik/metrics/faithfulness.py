from opik.evaluation.metrics import Hallucination
from evals.opik.judge_model import judge_model

THRESHOLD = 0.8

# Opik's built-in Hallucination metric returns 1.0 when hallucination IS
# detected and 0.0 when the output is faithful to the context -- the inverse
# polarity of DeepEval's FaithfulnessMetric / TruLens's Groundedness (both
# score higher = more faithful). Invert it here so THRESHOLD keeps the same
# "higher is better" meaning used across all three frameworks.
_metric = Hallucination(model=judge_model, track=False)


def score_faithfulness(input_text: str, actual_output: str, retrieval_context: list[str]) -> tuple[float, dict]:
    result = _metric.score(
        input=input_text,
        output=actual_output,
        context=retrieval_context,
    )
    faithfulness_score = 1.0 - result.value
    return faithfulness_score, {"reason": result.reason}
