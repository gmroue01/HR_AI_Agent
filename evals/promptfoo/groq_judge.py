import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "openai/gpt-oss-120b"
_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def score_criteria(criteria: str, fields: dict) -> dict:
    """
    Ask the judge model to score an interaction against a criteria description,
    GEval-style. Same judge model (Groq, openai/gpt-oss-120b) as
    evals/deepeval/groq_judge.py, evals/trulens/litellm_provider.py and
    evals/opik/judge_model.py — same rubric, same judge, fair benchmark across
    all four frameworks.

    Args:
        criteria: the grading rubric text.
        fields: labelled input/output fields to show the judge (input, actual
            output, retrieval context, etc.).

    Returns:
        dict: {"score": float in [0, 1], "reason": str}, consumed directly as a
        promptfoo python-assertion GradingResult (threshold applied by promptfoo).
    """
    fields_text = "\n\n".join(f"{label}:\n{value}" for label, value in fields.items())

    prompt = (
        "You are an expert evaluator grading an AI agent's response.\n\n"
        f"Criteria:\n{criteria}\n\n"
        f"{fields_text}\n\n"
        "Score how well the response satisfies the criteria, from 0.0 (completely "
        "fails the criteria) to 1.0 (fully satisfies the criteria). Respond with "
        "ONLY a JSON object in this exact form, no other text: "
        '{"score": <float between 0 and 1>, "reason": "<one or two sentence explanation>"}'
    )

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content.strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"score": 0.0, "reason": f"Judge returned unparseable output: {raw}"}

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"score": 0.0, "reason": f"Judge returned invalid JSON: {raw}"}

    score = float(parsed.get("score", 0.0))
    reason = str(parsed.get("reason", ""))
    return {"score": max(0.0, min(1.0, score)), "reason": reason}
