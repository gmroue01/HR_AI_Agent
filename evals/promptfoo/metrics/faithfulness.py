# Unlike the other metrics in this package, faithfulness is graded by
# promptfoo's own built-in "context-faithfulness" assertion (its RAG-triad
# faithfulness check — see https://promptfoo.dev/docs/configuration/expected-outputs/model-graded/context-faithfulness/)
# instead of a custom python judge — it's the promptfoo-native equivalent of
# evals/deepeval/metrics/faithfulness.py's FaithfulnessMetric, so there is no
# get_assert here. Wired directly in promptfooconfig.yaml via:
#   type: context-faithfulness
#   contextTransform: "context.metadata.retrieved_chunks"
#   threshold: 0.8
# Kept as its own file for structural parity with the other three frameworks,
# each of which has one metrics/faithfulness.py.
THRESHOLD = 0.8
