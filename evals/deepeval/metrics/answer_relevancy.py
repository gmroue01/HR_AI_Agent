from deepeval.metrics import AnswerRelevancyMetric
from evals.deepeval.groq_judge import GroqJudge

groq_judge = GroqJudge()

# QAG-based, like FaithfulnessMetric — decomposes the reply into statements
# and checks each is actually relevant to the input, instead of a single
# holistic GEval judgment. Complements Faithfulness (is the reply grounded
# in the retrieved context) with the other half of the RAG-answer question
# (does the reply actually address what was asked).
expense_answer_relevancy = AnswerRelevancyMetric(
    threshold=0.8,
    model=groq_judge,
    include_reason=True,
)
