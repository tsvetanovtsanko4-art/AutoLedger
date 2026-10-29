import { test, expect } from '@playwright/test';

test('landing page shows fleet statistics without logging in', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Track Your Fleet. Optimize Your Spend.' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Popularity by Manufacturer' })).toBeVisible();
});

test('signed-out visitors are sent to login from private pages', async ({ page }) => {
    await page.goto('/home');

    await expect(page).toHaveURL('/login');
});
