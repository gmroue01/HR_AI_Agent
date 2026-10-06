import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from helpers import LLM_TIMEOUT, login, wait


@pytest.fixture(autouse=True)
def logged_in(driver):
    login(driver, "Gabriel", "Mroue")


def _send(driver, text):
    chat_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInputTextArea']")
    chat_input.send_keys(text)
    chat_input.send_keys(Keys.ENTER)


def test_shows_an_empty_chat_input_after_login(driver):
    assert driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInputTextArea']").is_displayed()
    assert driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']") == []


def test_displays_the_user_message_after_sending_it(driver):
    _send(driver, "Hello, are you there?")

    wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stChatMessageAvatarUser']")))
    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']")
    assert "Hello, are you there?" in messages[0].text


def test_gets_a_non_empty_reply_from_the_assistant(driver):
    _send(driver, "Hello, are you there?")

    # LLM call + tool round-trips can take a while, so give it a generous timeout.
    wait(driver, LLM_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stChatMessageAvatarAssistant']"))
    )

    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']")
    reply = messages[-1].text
    assert len(reply.strip()) > 0


def test_shows_a_debug_trace_once_the_assistant_has_replied(driver):
    _send(driver, "Hello, are you there?")
    wait(driver, LLM_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stChatMessageAvatarAssistant']"))
    )

    expander = wait(driver).until(
        lambda d: next(
            (e for e in d.find_elements(By.CSS_SELECTOR, "[data-testid='stExpander']") if "Debug trace" in e.text),
            None,
        )
    )
    assert expander is not None

    expander.find_element(By.XPATH, ".//p[text()='Debug trace']").click()
    wait(driver).until(lambda d: expander.find_element(By.CSS_SELECTOR, "[data-testid='stJson']").is_displayed())


def test_keeps_both_messages_visible_after_a_full_exchange(driver):
    _send(driver, "Hello, are you there?")
    wait(driver, LLM_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stChatMessageAvatarAssistant']"))
    )

    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']")
    assert len(messages) == 2
