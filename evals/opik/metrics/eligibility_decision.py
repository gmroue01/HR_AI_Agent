from opik.evaluation.metrics import GEval
from evals.opik.judge_model import judge_model

THRESHOLD = 0.8

TASK_INTRODUCTION = (
    "You are evaluating an HR assistant's expense-eligibility decision "
    "against a retrieved expense policy."
)

# Same wording as evals/deepeval/metrics/eligibility_decision.py's GEval criteria,
# so all three frameworks judge this scenario against the same rubric.
EVALUATION_CRITERIA = (
    "Given the retrieved expense policy context, determine whether the "
    "agent's accept/refuse decision matches what the policy actually states. "
    "A correct decision must align with the specific article cited in the "
    "context, not general assumptions."
)

_metric = GEval(
    task_introduction=TASK_INTRODUCTION,
    evaluation_criteria=EVALUATION_CRITERIA,
    model=judge_model,
    name="Eligibility Decision Correctness",
    track=False,
)

# Public alias — evals/shared/regression_experiment.py reuses this exact
# GEval instance as an opik.evaluate() scoring metric, instead of
# constructing a second, possibly-drifting copy of the same judge/criteria.
metric = _metric


def score_eligibility_decision(input_text: str, actual_output: str, retrieval_context: list[str]) -> tuple[float, dict]:
    context_block = "\n---\n".join(retrieval_context)
    combined_output = (
        f"Retrieved policy context:\n{context_block}\n\n"
        f"User input:\n{input_text}\n\n"
        f"Agent response:\n{actual_output}"
    )
    result = _metric.score(output=combined_output)
    return result.value, {"reason": result.reason}
