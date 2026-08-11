import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.promptfoo.datasets.eu_ai_act_cases import EU_AI_ACT_CASES
from evals.promptfoo.metrics.eu_ai_act import THRESHOLD


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
                    "value": "file://metrics/eu_ai_act.py:get_assert",
                    "threshold": THRESHOLD,
                },
            ],
        }
        for case in EU_AI_ACT_CASES
    ]
