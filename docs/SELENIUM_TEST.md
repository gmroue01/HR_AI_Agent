This document gathers the test function documentation for the Selenium end-to-end suite in [`e2e_selenium/`](../e2e_selenium/).

This suite is a 1:1 port of [`PLAYWRIGHT_TEST.md`](./PLAYWRIGHT_TEST.md)'s `login.spec.ts` and `chat.spec.ts` : same 12 test cases, same assertions, same real Streamlit app and real Groq calls, driven with Selenium/`pytest` instead of Playwright/`@playwright/test`. The point isn't that one tool is "better" — both exercise the exact same UI behavior — it's to have a second, independent implementation of the same E2E coverage in Python instead of TypeScript, useful as a side-by-side comparison of the two tools for a QA audience deciding what to adopt.

**Why the tests aren't identical line-for-line.** Playwright's locators (`getByLabel`, `getByRole`) resolve accessible names for you; Selenium has no equivalent, so every locator here targets the raw DOM attribute Streamlit actually renders instead — `input[aria-label='Surname']`, `[data-testid='stChatMessage']`, `//button[.//p[text()='Login']]`. These were found by inspecting the real rendered page (see the pattern already used for the Playwright suite), not guessed from Streamlit's docs, since the DOM structure Streamlit emits for a given widget isn't officially stable API. Both suites end up depending on the same underlying markup, they just reach it through different APIs.

**Why the same hydration race showed up here too.** Just like in [`PLAYWRIGHT_TEST.md`](./PLAYWRIGHT_TEST.md), the very first interaction against a freshly (re)hydrated page could hit a `NoSuchElementException` on the "Surname" input — Streamlit's HTTP endpoint responds before its websocket-driven frontend has finished rendering the form. The fix is the same idea as Playwright's `expect: { timeout: 10_000 }`, done explicitly instead of implicitly : every test (and the shared `login()` helper) waits for `input[aria-label='Surname']` to be present with `WebDriverWait` before interacting with it, rather than assuming the DOM is ready right after `driver.get()`.

## Configuration ([`e2e_selenium/conftest.py`](../e2e_selenium/conftest.py))

- A session-scoped `streamlit_server` fixture mirrors Playwright's `webServer` : it checks `http://localhost:8501` first and reuses an already-running instance if found, otherwise spawns `streamlit run streamlit_app.py --server.headless true` as a subprocess and tears it down at the end of the session — so a server started manually during development isn't killed and restarted on every run, but `pytest e2e_selenium` still works standalone from a cold start.
- A function-scoped `driver` fixture creates a headless Chrome instance per test via Selenium 4's built-in Selenium Manager (no manual chromedriver download/pinning needed) and quits it afterward.
- Tests run sequentially by default (`pytest` doesn't parallelize without `-n`/`pytest-xdist`), avoiding the concurrent-session flakiness against the single dev Streamlit instance that [`PLAYWRIGHT_TEST.md`](./PLAYWRIGHT_TEST.md) had to fix explicitly with `workers: 1`.
- Shared locators and the `login()` helper live in [`e2e_selenium/helpers.py`](../e2e_selenium/helpers.py).

Run with `pytest e2e_selenium -v`.

## [`test_login.py`](../e2e_selenium/test_login.py)

**Objective** : same as Playwright's `login.spec.ts` — verify `show_login()` (`streamlit_app.py`) authenticates against `backend/auth.py::login()` correctly and reflects both success and failure in the UI, against the same seeded rows (`surname='Gabriel', name='Mroue'` → employee; `surname='Lisa', name='Bodson'` → HR), including the same reversed-order greeting (`"Hello Mroue Gabriel..."`).

- **`test_displays_the_login_form`** — the "Login" `<h1>`, both inputs, and the submit button are visible before any input.
- **`test_logs_in_an_employee_with_valid_credentials`** / **`test_logs_in_an_hr_user_with_valid_credentials`** — a valid surname/name pair reaches the chat screen and shows the expected name and role in `[data-testid='stCaptionContainer']`.
- **`test_shows_an_error_for_unknown_credentials`** — an unrecognized pair shows the `[data-testid='stAlert']` text "No Employee found" and stays on the login screen.
- **`test_shows_an_error_when_fields_are_left_empty`** — submitting blank fields behaves like unknown credentials.
- **`test_is_case_sensitive_on_surname_and_name`** — a differently-cased pair is rejected, same plain SQL equality match as the Playwright suite exercises.
- **`test_allows_logging_out_after_a_successful_login`** — clicking "Disconnect" returns to the login screen. Waits for the `<h1>` text itself to become "Login" (re-querying the element on every poll) rather than just its presence, since the old "HR Agent" heading is still present in the DOM for a moment after the click, before Streamlit's rerun replaces it.

## [`test_chat.py`](../e2e_selenium/test_chat.py)

**Objective** : same as Playwright's `chat.spec.ts` — verify the chat UI in `show_chat()` sends a message, renders it, and eventually renders a non-empty reply, a structural check rather than a judgment of what the model said.

Every test logs in first (as `Gabriel`/`Mroue`) via an autouse `logged_in` fixture wrapping `helpers.login()`. Locators reuse the same `data-testid` attributes as the Playwright suite (`stChatInputTextArea`, `stChatMessage`, `stChatMessageAvatarUser`/`stChatMessageAvatarAssistant`, `stExpander`, `stJson`), confirmed to be identical markup by inspecting a real send-message round trip.

- **`test_shows_an_empty_chat_input_after_login`** — the chat input is visible and no message bubbles exist yet.
- **`test_displays_the_user_message_after_sending_it`** — sending a message renders it immediately with the user avatar.
- **`test_gets_a_non_empty_reply_from_the_assistant`** — a 30s wait (`LLM_TIMEOUT`) for the assistant avatar to appear, same rationale as the Playwright suite : real Groq call plus tool-call round-trips can exceed the default 10s.
- **`test_shows_a_debug_trace_once_the_assistant_has_replied`** — finds the "Debug trace" expander, clicks its header to expand it, and waits for `[data-testid='stJson']` to become visible.
- **`test_keeps_both_messages_visible_after_a_full_exchange`** — exactly two `stChatMessage` bubbles exist after one exchange.

Same trade-off as the Playwright suite : every chat test hits the real Groq API, so it's neither free nor deterministic — see [`MOCKING_TEST.md`](./MOCKING_TEST.md) for the alternative that tests the surrounding orchestration logic without it.

## [`test_judge.py`](../e2e_selenium/test_judge.py)

**Objective** : the Python counterpart to `judge.spec.ts` (see [`PLAYWRIGHT_TEST.md`](./PLAYWRIGHT_TEST.md)) — capture the reply exactly as rendered in a real Selenium-driven browser session and run it through an actual LLM-as-judge metric, instead of only checking that a reply exists.

Where the Playwright version needed a custom `OpikBaseModel` subclass to talk to Groq (no Groq provider in Opik's TS SDK), this one needs nothing new : Selenium and DeepEval are both plain Python/pytest here, so `evals/deepeval/groq_judge.py`'s existing `GroqJudge` is reused directly as the model for a `GEval` metric (`HR Reply Quality`, same criteria as the Playwright version — coherent, on-topic for an HR assistant, not an error/refusal).

- **`test_the_reply_rendered_in_the_browser_passes_an_llm_as_judge_quality_check`** — sends a message, waits for the assistant reply, scores it with `GEval`, asserts `reply_quality.score >= 0.7`.

Locator note : the reply is read from `messages[-1].find_element(By.CSS_SELECTOR, "[data-testid='stChatMessageContent']").text`, not the whole `stChatMessage` bubble — `test_chat.py`'s tests read the whole bubble safely since they only check non-empty length, but the whole bubble also contains the assistant avatar's Material icon, which renders as literal ligature text (`"smart_toy"`) that a judge would otherwise score as if it were part of the reply. This exact bug was caught for real running `judge.spec.ts` first ; scoping to `stChatMessageContent` here from the start avoided repeating it.
