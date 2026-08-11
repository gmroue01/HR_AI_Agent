import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.promptfoo.datasets.robustness_cases import ROBUSTNESS_CASES
from evals.promptfoo.metrics.robustness import THRESHOLD


def generate_tests(config=None):
    return [
        {
            "description": case["name"],
            "vars": {
                "query": case["input"],
                "user_role": case["user_role"],
            },
            "assert": [
                {
                    "type": "python",
                    "value": "file://metrics/robustness.py:get_assert",
                    "threshold": THRESHOLD,
                },
            ],
        }
        for case in ROBUSTNESS_CASES
    ]
