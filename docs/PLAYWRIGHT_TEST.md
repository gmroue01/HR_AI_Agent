This document gathers the test function documentation for the Playwright end-to-end suite in [`e2e/`](../e2e/).

Unlike every other suite in this project, this one does not import the agent's Python code at all. It drives the real `streamlit_app.py` UI in a real Chromium browser : filling in the login form, sending chat messages, reading back whatever renders on screen. That makes it the only suite that verifies the actual application people use — the login form, the SQLite-backed auth in `backend/auth.py`, the chat UI, the real Groq API call — wired together correctly, as opposed to [`MOCKING_TEST.md`](./MOCKING_TEST.md)'s suite (which mocks the model call and never touches the browser) or the DeepEval/TruLens/Opik suites (which judge answer quality, not UI behavior).

One consequence of testing through the browser is that the LLM call in `chatbot_core.run_agent_turn()` happens server-side, inside the Streamlit Python process — there is no client-side `fetch`/`XHR` for Playwright's `page.route()` to intercept, so this suite cannot mock the model the way [`MOCKING_TEST.md`](./MOCKING_TEST.md) does. Every chat test here calls the real Groq API.

## Configuration ([`playwright.config.ts`](../playwright.config.ts))

- `testDir: './e2e'`, `baseURL: 'http://localhost:8501'` (Streamlit's default port).
- `webServer` runs `streamlit run streamlit_app.py --server.headless true` before the suite and reuses an already-running instance outside CI (`reuseExistingServer: !process.env.CI`), so a server started manually during development isn't killed and restarted on every run.
- `workers: 1` — the Streamlit dev server is a single instance; running several browser sessions against it concurrently was observed to be flaky (dropped websocket connections, "Connection error" dialogs), so tests run sequentially instead.
- `expect: { timeout: 10_000 }` — Streamlit's HTTP endpoint answers the `webServer` health check as soon as the process is up, but the frontend then needs a few more seconds to hydrate over its websocket connection. The default 5s assertion timeout was intermittently too short for the very first test hitting a freshly started server; 10s absorbs that without slowing down the (already-hydrated) tests that follow.

Run with `npm run test:e2e` (or `npm run test:e2e:ui` for the interactive UI mode).

## [`login.spec.ts`](../e2e/login.spec.ts)

**Objective** : Verify the login form in `show_login()` (`streamlit_app.py`) authenticates against `backend/auth.py::login()` correctly and reflects both success and failure in the UI.

Logs in against real rows seeded in `backend/app.db` (e.g. `surname='Gabriel', name='Mroue'` → role `employee`; `surname='Lisa', name='Bodson'` → role `HR`). Note the DB's `surname`/`name` columns are populated in reversed order from what the names suggest, so the post-login greeting reads `"Hello Mroue Gabriel..."`, not `"Hello Gabriel Mroue..."` — the tests assert the actual rendered order, not the intuitive one.

- **`displays the login form`** — the "Login" heading, both form fields, and the submit button are visible before any input.
- **`logs in an employee with valid credentials`** / **`logs in an HR user with valid credentials`** — a valid surname/name pair reaches the chat screen and shows the expected name and role.
- **`shows an error for unknown credentials`** — an unrecognized pair shows "No Employee found" and stays on the login screen.
- **`shows an error when fields are left empty`** — submitting blank fields behaves like unknown credentials (no employee has empty surname/name).
- **`is case-sensitive on surname and name`** — the lookup in `auth.py` is a plain SQL equality match, so a differently-cased pair that would otherwise be valid is rejected.
- **`allows logging out after a successful login`** — the "Disconnect" button returns to the login screen.

Field locators use `getByLabel(..., { exact: true })` — without `exact`, `getByLabel('Name')` also matches the "Surname" field, since Playwright's label matching is substring-based by default and "Surname" contains "Name".

## [`chat.spec.ts`](../e2e/chat.spec.ts)

**Objective** : Verify the chat UI in `show_chat()` (`streamlit_app.py`) sends a message, renders it, and eventually renders a non-empty reply from the agent — a structural check ("did the model respond at all") rather than a judgment of what it said, which is what the LLM-as-a-judge suites are for.

Every test logs in first (as the employee `Gabriel`/`Mroue`) via a shared `login()` helper. Locators use Streamlit's internal `data-testid` attributes (`stChatInputTextArea`, `stChatMessage`, `stChatMessageAvatarUser`/`stChatMessageAvatarAssistant`, `stExpander`, `stJson`) rather than visible text, since they're stable across message content and don't depend on English/French wording.

- **`shows an empty chat input after login`** — the chat input is visible and no message bubbles exist yet.
- **`displays the user message after sending it`** — sending a message renders it immediately in a `stChatMessage` bubble with the user avatar.
- **`gets a non-empty reply from the assistant`** — after sending a message, an assistant-avatar bubble eventually appears with non-empty text. Uses a 30s timeout on this assertion, since a real Groq call (plus any tool-call round-trips inside `run_agent_turn()`) can take noticeably longer than the suite's default 10s.
- **`shows a debug trace once the assistant has replied`** — the "Debug trace" expander (rendering `trace` from `run_agent_turn()`) is present and expands to show its JSON content.
- **`keeps both messages visible after a full exchange`** — after one exchange, exactly two `stChatMessage` bubbles exist (one user, one assistant).

Because these tests hit the real API, they consume Groq quota on every run and their duration depends on real model latency — that's an intentional trade-off for testing the actual end-to-end path; see [`MOCKING_TEST.md`](./MOCKING_TEST.md) for the free, deterministic alternative that tests the surrounding orchestration logic without it.
