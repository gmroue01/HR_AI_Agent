import { test, expect, Page } from '@playwright/test';

async function login(page: Page, surname: string, name: string) {
  await page.goto('/');
  await page.getByLabel('Surname', { exact: true }).fill(surname);
  await page.getByLabel('Name', { exact: true }).fill(name);
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page.getByRole('button', { name: 'Disconnect' })).toBeVisible();
}

test.describe('Chatbot', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'Gabriel', 'Mroue');
  });

  test('shows an empty chat input after login', async ({ page }) => {
    await expect(page.getByTestId('stChatInputTextArea')).toBeVisible();
    await expect(page.getByTestId('stChatMessage')).toHaveCount(0);
  });

  test('displays the user message after sending it', async ({ page }) => {
    await page.getByTestId('stChatInputTextArea').fill('Hello, are you there?');
    await page.getByTestId('stChatInputTextArea').press('Enter');

    await expect(page.getByTestId('stChatMessageAvatarUser')).toBeVisible();
    await expect(page.getByTestId('stChatMessage').first()).toContainText('Hello, are you there?');
  });

  test('gets a non-empty reply from the assistant', async ({ page }) => {
    await page.getByTestId('stChatInputTextArea').fill('Hello, are you there?');
    await page.getByTestId('stChatInputTextArea').press('Enter');

    // LLM call + tool round-trips can take a while, so give it a generous timeout.
    await expect(page.getByTestId('stChatMessageAvatarAssistant')).toBeVisible({ timeout: 30_000 });

    const reply = await page.getByTestId('stChatMessage').last().innerText();
    expect(reply.trim().length).toBeGreaterThan(0);
  });

  test('shows a debug trace once the assistant has replied', async ({ page }) => {
    await page.getByTestId('stChatInputTextArea').fill('Hello, are you there?');
    await page.getByTestId('stChatInputTextArea').press('Enter');
    await expect(page.getByTestId('stChatMessageAvatarAssistant')).toBeVisible({ timeout: 30_000 });

    const traceExpander = page.getByTestId('stExpander').filter({ hasText: 'Debug trace' });
    await expect(traceExpander).toBeVisible();

    await traceExpander.getByText('Debug trace').click();
    await expect(traceExpander.getByTestId('stJson')).toBeVisible();
  });

  test('keeps both messages visible after a full exchange', async ({ page }) => {
    await page.getByTestId('stChatInputTextArea').fill('Hello, are you there?');
    await page.getByTestId('stChatInputTextArea').press('Enter');
    await expect(page.getByTestId('stChatMessageAvatarAssistant')).toBeVisible({ timeout: 30_000 });

    await expect(page.getByTestId('stChatMessage')).toHaveCount(2);
  });
});
