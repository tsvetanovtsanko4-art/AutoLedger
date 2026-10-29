import { test, expect } from '@playwright/test';
import { registerNewUser } from './helpers';

test('new user registers and lands in an empty garage', async ({ page }) => {
    const { email } = await registerNewUser(page);

    await expect(page.getByText('Your garage is empty')).toBeVisible();
    await expect(page.getByText(`Hi, ${email}`)).toBeVisible();
});

test('user can log out and log back in', async ({ page }) => {
    const { email, password } = await registerNewUser(page);

    await page.getByRole('button', { name: 'Logout' }).click();
    await page.goto('/home');
    await expect(page).toHaveURL('/login');

    await page.getByTestId('input-email').fill(email);
    await page.getByTestId('input-password').fill(password);
    await page.getByTestId('btn-login').click();
    await expect(page).toHaveURL('/home');
});

test('wrong password shows an error and stays on the login page', async ({ page }) => {
    const { email } = await registerNewUser(page);
    await page.getByRole('button', { name: 'Logout' }).click();

    await page.goto('/login');
    await page.getByTestId('input-email').fill(email);
    await page.getByTestId('input-password').fill('wrong-password');
    await page.getByTestId('btn-login').click();

    await expect(page.getByTestId('login-error')).toContainText('Incorrect email or password');
    await expect(page).toHaveURL('/login');
});

test('register form validates before calling the API', async ({ page }) => {
    await page.goto('/register');
    await page.getByTestId('input-email').fill('not-an-email');
    await page.getByTestId('btn-register').click();

    await expect(page.getByTestId('error-email')).toBeVisible();
    await expect(page.getByTestId('error-password')).toHaveText('Password is required.');
});
