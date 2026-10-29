import { test, expect } from '@playwright/test';
import { addCar, logRefueling, registerNewUser, uniqueId } from './helpers';

test.beforeEach(async ({ page }) => {
    await registerNewUser(page);
});

test('added car shows up in the garage with an upper-case plate', async ({ page }) => {
    const plate = `ca${uniqueId().slice(-6)}`.toLowerCase();

    await addCar(page, { plate });

    await expect(page).toHaveURL('/home');
    await expect(page.getByText(plate.toUpperCase())).toBeVisible();
});

test('a plate that is already registered is flagged on the form', async ({ page }) => {
    const plate = `CB${uniqueId().slice(-6)}`;
    await addCar(page, { plate });
    await expect(page).toHaveURL('/home');

    await addCar(page, { plate: plate.toLowerCase() });

    await expect(page.getByText('This plate number is already registered')).toBeVisible();
    await expect(page).toHaveURL('/add-car');
});

test('two refuelings give an average consumption', async ({ page }) => {
    await addCar(page, { plate: `PB${uniqueId().slice(-6)}`, odometer: 1000 });
    await page.locator('[data-testid^="car-card-"]').first().click();

    await logRefueling(page, { odometer: 1000, liters: 40 });
    await logRefueling(page, { odometer: 1500, liters: 35 });  // 35 L over 500 km

    await expect(page.getByText('7.0 L/100km')).toBeVisible();
    await page.getByRole('link', { name: 'My Garage' }).click();
    await expect(page.getByText('7 L/100km')).toBeVisible();
});

test('refueling with a negative cost shows the validation message', async ({ page }) => {
    await addCar(page, { plate: `KH${uniqueId().slice(-6)}` });
    await page.locator('[data-testid^="car-card-"]').first().click();

    await logRefueling(page, { odometer: 20000, liters: 30, cost: '-5' });

    await expect(page.getByText(/cost_eur: Input should be greater than 0/)).toBeVisible();
});

test('favourite car moves to the top of the garage', async ({ page }) => {
    await addCar(page, { plate: `E${uniqueId().slice(-6)}` });
    await addCar(page, { plate: `M${uniqueId().slice(-6)}` });
    const cards = page.locator('[data-testid^="car-card-"]');
    const secondCar = await cards.nth(1).getAttribute('data-testid');

    await cards.nth(1).getByTitle('Add to favorites').click();

    await expect(cards.first()).toHaveAttribute('data-testid', secondCar);
    await expect(cards.first().getByText('FAVORITE')).toBeVisible();
});
