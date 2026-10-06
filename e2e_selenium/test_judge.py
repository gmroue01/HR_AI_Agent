import pytest
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from helpers import LLM_TIMEOUT, login, wait
from evals.deepeval.groq_judge import GroqJudge

"""
The Python counterpart to e2e/judge.spec.ts (Playwright + Opik): captures the
reply exactly as rendered in a real Selenium-driven browser session and runs
it through an actual LLM-as-judge metric, the same kind of check the
DeepEval/TruLens/Opik/Promptfoo suites run directly against
chatbot_core.run_agent_turn() in Python (see TESTING_OVERVIEW.md).

Unlike judge.spec.ts, this needs no custom model wrapper — GroqJudge already
exists for the rest of the DeepEval suite (evals/deepeval/groq_judge.py),
since Selenium and DeepEval both just run as plain Python/pytest here.
"""

QUALITY_THRESHOLD = 0.7

reply_quality = GEval(
    name="HR Reply Quality",
    criteria=(
        "The reply must be coherent, in plain language, on-topic for an HR "
        "assistant (salary, wellness, expenses, HR policy, or confidential "
        "project access), and must not be an error message, a refusal "
        "without explanation, or unrelated content."
    ),
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=QUALITY_THRESHOLD,
    model=GroqJudge(),
)


@pytest.fixture(autouse=True)
def logged_in(driver):
    login(driver, "Gabriel", "Mroue")


def test_the_reply_rendered_in_the_browser_passes_an_llm_as_judge_quality_check(driver):
    message = "Hello, are you there?"
    chat_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInputTextArea']")
    chat_input.send_keys(message)
    chat_input.send_keys(Keys.ENTER)

    wait(driver, LLM_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stChatMessageAvatarAssistant']"))
    )

    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']")

    reply = messages[-1].find_element(By.CSS_SELECTOR, "[data-testid='stChatMessageContent']").text
    assert len(reply.strip()) > 0

    test_case = LLMTestCase(input=message, actual_output=reply)
    reply_quality.measure(test_case, _show_indicator=False)

    assert reply_quality.score >= QUALITY_THRESHOLD, (
        f"GEval scored the real UI reply \"{reply}\" at {reply_quality.score} "
        f"(< {QUALITY_THRESHOLD}): {reply_quality.reason}"
    )
