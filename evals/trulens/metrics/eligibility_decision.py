from evals.trulens.litellm_provider import provider

THRESHOLD = 0.8


CRITERIA = (
    "Given the retrieved expense policy context, determine whether the "
    "agent's accept/refuse decision matches what the policy actually states. "
    "A correct decision must align with the specific article cited in the "
    "context, not general assumptions."
)


def score_eligibility_decision(input_text: str, actual_output: str, retrieval_context: list[str]) -> tuple[float, dict]:
    context_block = "\n---\n".join(retrieval_context)
    system_prompt = (
        f"{CRITERIA}\n\n"
        f"Retrieved policy context:\n{context_block}\n\n"
        f"User input:\n{input_text}\n\n"
        f"Agent response:\n{actual_output}\n\n"
        "Respond with a JSON object containing a score between 0 and 10 and a reason."
    )
    return provider.generate_score_and_reasons(system_prompt=system_prompt)
