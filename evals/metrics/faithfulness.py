from deepeval.metrics import FaithfulnessMetric
from evals.groq_judge import GroqJudge

groq_judge = GroqJudge()

expense_faithfulness = FaithfulnessMetric(
    threshold=0.8,
    model=groq_judge,
    include_reason=True,
)
