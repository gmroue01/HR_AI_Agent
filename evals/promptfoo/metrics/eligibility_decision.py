import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evals.promptfoo.groq_judge import score_criteria

# Same rubric text as evals/deepeval/metrics/eligibility_decision.py,
# evals/trulens/metrics/eligibility_decision.py and evals/opik/metrics/eligibility_decision.py.
CRITERIA = (
    "Given the retrieved expense policy context, determine whether the "
    "agent's accept/refuse decision matches what the policy actually states. "
    "A correct decision must align with the specific article cited in the "
    "context, not general assumptions."
)
THRESHOLD = 0.8


def get_assert(output, context):
    vars_ = (context or {}).get("vars", {}) or {}
    metadata = (context or {}).get("metadata", {}) or {}
    retrieval_context = metadata.get("retrieved_chunks", [])

    return score_criteria(
        CRITERIA,
        {
            "User input": vars_.get("query", ""),
            "Agent's actual output": output,
            "Retrieved policy context": "\n\n".join(retrieval_context) or "(none retrieved)",
        },
    )
