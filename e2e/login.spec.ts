import { test, expect } from '@playwright/test';

test.describe('Login page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays the login form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
    await expect(page.getByLabel('Surname', { exact: true })).toBeVisible();
    await expect(page.getByLabel('Name', { exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
  });

  test('logs in an employee with valid credentials', async ({ page }) => {
    await page.getByLabel('Surname', { exact: true }).fill('Gabriel');
    await page.getByLabel('Name', { exact: true }).fill('Mroue');
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByText('Hello Mroue Gabriel. You are the (employee)')).toBeVisible();
  });

  test('logs in an HR user with valid credentials', async ({ page }) => {
    await page.getByLabel('Surname', { exact: true }).fill('Lisa');
    await page.getByLabel('Name', { exact: true }).fill('Bodson');
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByText('Hello Bodson Lisa. You are the (HR)')).toBeVisible();
  });

  test('shows an error for unknown credentials', async ({ page }) => {
    await page.getByLabel('Surname', { exact: true }).fill('Unknown');
    await page.getByLabel('Name', { exact: true }).fill('Person');
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByText('No Employee found')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
  });

  test('shows an error when fields are left empty', async ({ page }) => {
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByText('No Employee found')).toBeVisible();
  });

  test('is case-sensitive on surname and name', async ({ page }) => {
    await page.getByLabel('Surname', { exact: true }).fill('gabriel');
    await page.getByLabel('Name', { exact: true }).fill('mroue');
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByText('No Employee found')).toBeVisible();
  });

  test('allows logging out after a successful login', async ({ page }) => {
    await page.getByLabel('Surname', { exact: true }).fill('Gabriel');
    await page.getByLabel('Name', { exact: true }).fill('Mroue');
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByRole('button', { name: 'Disconnect' })).toBeVisible();
    await page.getByRole('button', { name: 'Disconnect' }).click();

    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
  });
});
