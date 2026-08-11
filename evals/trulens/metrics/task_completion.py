from evals.trulens.litellm_provider import provider

THRESHOLD = 0.8


CRITERIA = (
    "Given the task the agent was expected to accomplish, determine whether "
    "the agent's response and actions fully complete it. Partial completion "
    "(e.g. addressing only one part of a multi-part request) must not be "
    "scored as full completion."
)


def score_task_completion(input_text: str, actual_output: str, task: str, tools_called: list[str] = None) -> tuple[float, dict]:

    tools_block = ", ".join(tools_called) if tools_called else "(none)"
    system_prompt = (
        f"{CRITERIA}\n\n"
        f"Expected task:\n{task}\n\n"
        f"User input:\n{input_text}\n\n"
        f"Tools called by the agent:\n{tools_block}\n\n"
        f"Agent response:\n{actual_output}\n\n"
        "Respond with a JSON object containing a score between 0 and 10 and a reason."
    )
    return provider.generate_score_and_reasons(system_prompt=system_prompt)
