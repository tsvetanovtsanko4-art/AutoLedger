import { expect } from '@playwright/test';

// Tests share one database, so every user and plate gets a unique suffix.
export function uniqueId() {
    return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`.toUpperCase();
}

export async function registerNewUser(page) {
    const email = `e2e-${uniqueId().toLowerCase()}@example.com`;
    const password = 'secret123';
    await page.goto('/register');
    await page.getByTestId('input-email').fill(email);
    await page.getByTestId('input-password').fill(password);
    await page.getByTestId('input-confirm-password').fill(password);
    await page.getByTestId('btn-register').click();
    await expect(page).toHaveURL('/home');
    return { email, password };
}

export async function addCar(page, { plate, vin = `WVW${uniqueId()}`, odometer = 10000 }) {
    await page.goto('/add-car');
    await page.getByTestId('input-plate').fill(plate);
    await page.getByTestId('input-make').fill('Skoda');
    await page.getByTestId('input-model').fill('Octavia');
    await page.locator('input[name="current_odometer"]').fill(String(odometer));
    await page.locator('input[name="vin"]').fill(vin);
    await page.getByTestId('btn-submit-car').click();
}

export async function logRefueling(page, { odometer, liters, cost = '70' }) {
    await page.getByRole('link', { name: '+ Log Fuel' }).click();
    await page.getByTestId('input-fuel-date').fill('2026-03-01');
    await page.getByTestId('input-cost').fill(cost);
    await page.getByTestId('input-quantity').fill(String(liters));
    await page.getByTestId('input-odometer').fill(String(odometer));
    await page.getByTestId('btn-submit-refuel').click();
}
