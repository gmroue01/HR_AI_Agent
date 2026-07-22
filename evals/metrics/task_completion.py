from deepeval.metrics import TaskCompletionMetric
from evals.groq_judge import GroqJudge

groq_judge = GroqJudge()

task_completion = TaskCompletionMetric(
    threshold=0.8,
    model=groq_judge,
    include_reason=True,
)
