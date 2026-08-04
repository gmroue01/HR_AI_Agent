from opik.evaluation.metrics import GEval
from evals.opik.judge_model import judge_model

THRESHOLD = 0.8

TASK_INTRODUCTION = (
    "You are evaluating whether an HR assistant fully completed the task "
    "its user asked for."
)

# DeepEval's TaskCompletionMetric (evals/deepeval/metrics/task_completion.py) is a
# built-in metric with no exposed criteria text to mirror, so this rubric is
# authored fresh — same wording already used in evals/trulens/metrics/task_completion.py,
# reused here for consistency across all three frameworks.
EVALUATION_CRITERIA = (
    "Given the task the agent was expected to accomplish, determine whether "
    "the agent's response and actions fully complete it. Partial completion "
    "(e.g. addressing only one part of a multi-part request) must not be "
    "scored as full completion."
)

_metric = GEval(
    task_introduction=TASK_INTRODUCTION,
    evaluation_criteria=EVALUATION_CRITERIA,
    model=judge_model,
    name="Task Completion",
    track=False,
)


def score_task_completion(input_text: str, actual_output: str, task: str, tools_called: list[str] = None) -> tuple[float, dict]:
    # Some verification/side-effect steps (e.g. an access-code check) happen
    # inside a tool call, not in the visible reply text — the judge needs the
    # tool call list to credit those.
    tools_block = ", ".join(tools_called) if tools_called else "(none)"
    combined_output = (
        f"Expected task:\n{task}\n\n"
        f"User input:\n{input_text}\n\n"
        f"Tools called by the agent:\n{tools_block}\n\n"
        f"Agent response:\n{actual_output}"
    )
    result = _metric.score(output=combined_output)
    return result.value, {"reason": result.reason}
