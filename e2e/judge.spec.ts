import { test, expect, Page } from '@playwright/test';
import { GEval } from 'opik';
import { GroqJudgeModel } from './groq-judge-model';

/**
 * Every other Playwright spec checks structure — did a reply appear, is it
 * non-empty (see chat.spec.ts). This file goes one step further: it takes
 * the reply exactly as rendered in the real browser session and runs it
 * through an actual LLM-as-judge metric, the same kind of check the
 * DeepEval/TruLens/Opik/Promptfoo suites run directly against
 * chatbot_core.run_agent_turn() in Python (see TESTING_OVERVIEW.md).
 *
 * This is possible without a Python bridge because Opik ships a real
 * TypeScript SDK with genuine judge metrics (GEval, Hallucination,
 * AnswerRelevance, ...), not just tracing — see groq-judge-model.ts for the
 * Groq provider it doesn't ship out of the box.
 */
async function login(page: Page, surname: string, name: string) {
  await page.goto('/');
  await page.getByLabel('Surname', { exact: true }).fill(surname);
  await page.getByLabel('Name', { exact: true }).fill(name);
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page.getByRole('button', { name: 'Disconnect' })).toBeVisible();
}

const replyQuality = new GEval({
  name: 'HR Reply Quality',
  taskIntroduction:
    'You are grading a reply from an HR assistant chatbot to an employee message.',
  evaluationCriteria:
    'The reply must be coherent, in plain language, on-topic for an HR assistant ' +
    '(salary, wellness, expenses, HR policy, or confidential project access), and must ' +
    'not be an error message, a refusal without explanation, or unrelated content.',
  model: new GroqJudgeModel(),
});

const QUALITY_THRESHOLD = 0.7;

test.describe('LLM-as-judge on the real UI output', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'Gabriel', 'Mroue');
  });

  test('the reply rendered in the browser passes an LLM-as-judge quality check', async ({ page }) => {
    await page.getByTestId('stChatInputTextArea').fill('Hello, are you there?');
    await page.getByTestId('stChatInputTextArea').press('Enter');

    await expect(page.getByTestId('stChatMessageAvatarAssistant')).toBeVisible({ timeout: 30_000 });
    // stChatMessage also contains the avatar, whose Material icon renders as
    // literal ligature text ("smart_toy") in innerText — scoping to
    // stChatMessageContent excludes it so the judge only sees the actual reply.
    const reply = await page.getByTestId('stChatMessage').last().getByTestId('stChatMessageContent').innerText();
    expect(reply.trim().length).toBeGreaterThan(0);

    const result = await replyQuality.score({ output: reply });

    expect(
      result.value,
      `GEval scored the real UI reply "${reply}" at ${result.value} (< ${QUALITY_THRESHOLD}): ${result.reason}`,
    ).toBeGreaterThanOrEqual(QUALITY_THRESHOLD);
  });
});
