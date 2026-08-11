# Equivalent of DeepEval's ToolCorrectnessMetric(threshold=1.0) (used in
# evals/deepeval/test_expense_eligibility.py and test_confidential_access.py,
# mirrored the same way by TruLens and Opik): the agent must have called exactly
# the expected set of tools, no more, no fewer. threshold=1.0 is set on the
# promptfoo assertion itself (score must be exactly 1.0 to pass).
THRESHOLD = 1.0


def get_assert(output, context):
    vars_ = (context or {}).get("vars", {}) or {}
    metadata = (context or {}).get("metadata", {}) or {}

    expected = set(vars_.get("expected_tools", []) or [])
    actual = {t.get("name") for t in metadata.get("tools_called", [])}

    passed = actual == expected
    return {
        "score": 1.0 if passed else 0.0,
        "reason": f"Expected tools {sorted(expected)}, agent called {sorted(actual)}.",
    }
