
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from evals.groq_judge import GroqJudge

groq_judge = GroqJudge()

eligibility_decision_correctness = GEval(
    name="Eligibility Decision Correctness",
    criteria=(
        "Given the retrieved expense policy context, determine whether the "
        "agent's accept/refuse decisi   on matches what the policy actually states. "
        "A correct decision must align with the specific article cited in the "
        "context, not general assumptions."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT,
    ],
    threshold=0.8,
    model=groq_judge,
)
