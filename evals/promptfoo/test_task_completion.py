import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.promptfoo.datasets.task_completion_cases import TASK_COMPLETION_CASES
from evals.promptfoo.metrics.task_completion import THRESHOLD


def generate_tests(config=None):
    return [
        {
            "description": case["name"],
            "vars": {
                "query": case["input"],
                "user_role": case["user_role"],
                "task": case["task"],
            },
            "assert": [
                {
                    "type": "python",
                    "value": "file://metrics/task_completion.py:get_assert",
                    "threshold": THRESHOLD,
                },
            ],
        }
        for case in TASK_COMPLETION_CASES
    ]
