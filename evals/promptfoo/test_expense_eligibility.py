import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.promptfoo.datasets.expense_eligibility_cases import EXPENSE_ELIGIBILITY_CASES
from evals.promptfoo.metrics.eligibility_decision import THRESHOLD as ELIGIBILITY_THRESHOLD
from evals.promptfoo.metrics.faithfulness import THRESHOLD as FAITHFULNESS_THRESHOLD
from evals.promptfoo.metrics.tool_correctness import THRESHOLD as TOOL_THRESHOLD


def generate_tests(config=None):
    return [
        {
            "description": case["name"],
            "vars": {
                "query": case["input"],
                "user_role": case["user_role"],
                "expected_tools": case["expected_tools"],
            },
            "assert": [
                {
                    "type": "python",
                    "value": "file://metrics/tool_correctness.py:get_assert",
                    "threshold": TOOL_THRESHOLD,
                },
                {
                    "type": "context-faithfulness",
                    "contextTransform": "context.metadata.retrieved_chunks",
                    "threshold": FAITHFULNESS_THRESHOLD,
                },
                {
                    "type": "python",
                    "value": "file://metrics/eligibility_decision.py:get_assert",
                    "threshold": ELIGIBILITY_THRESHOLD,
                },
            ],
        }
        for case in EXPENSE_ELIGIBILITY_CASES
    ]
