import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evals.promptfoo.groq_judge import score_criteria

# DeepEval's TaskCompletionMetric (evals/deepeval/metrics/task_completion.py) is a
# built-in algorithm, not a GEval criteria string — there is nothing to copy
# verbatim here. This rubric is this project's own approximation of the same
# question ("did the agent complete the stated task end-to-end"), graded by the
# same judge model for cross-framework comparability.
CRITERIA = (
    "Determine whether the agent successfully completed the user's stated task "
    "end-to-end: addressing every part of the request, using its available tools "
    "and retrieved information where appropriate, and clearly reporting the "
    "outcome back to the user."
)
THRESHOLD = 0.8


def get_assert(output, context):
    vars_ = (context or {}).get("vars", {}) or {}

    return score_criteria(
        CRITERIA,
        {
            "User input": vars_.get("query", ""),
            "Task to accomplish": vars_.get("task", ""),
            "Agent's actual output": output,
        },
    )
