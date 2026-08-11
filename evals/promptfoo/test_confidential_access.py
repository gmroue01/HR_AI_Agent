import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.promptfoo.datasets.confidential_access_cases import CONFIDENTIAL_ACCESS_CASES
from evals.promptfoo.metrics.refusal_correctness import THRESHOLD as REFUSAL_THRESHOLD
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
                    "type": "python",
                    "value": "file://metrics/refusal_correctness.py:get_assert",
                    "threshold": REFUSAL_THRESHOLD,
                },
            ],
        }
        for case in CONFIDENTIAL_ACCESS_CASES
    ]
