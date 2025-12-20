import { test, expect } from '@playwright/test';

test.describe('ATLAS v18 Smoke Tests', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await expect(page.getByText('Synchronizing v18 clusters...')).not.toBeVisible({ timeout: 15000 });
    });

    test('Homepage maintains layout', async ({ page }) => {
        // Check for the header text which is always visible after loading
        await expect(page.locator('h2')).toBeVisible();
        // Check for branding
        await expect(page.getByText(/ATLAS/i).first()).toBeVisible();
    });

    test('Governance view loads', async ({ page }) => {
        // Find link/button by text
        await page.locator('button:has-text("Governance")').first().click();
        await expect(page.locator('h2')).toContainText('governance');
    });

    test('Feed view loads content', async ({ page }) => {
        // Check for "QFS Node Network" which is in DistributedFeed component
        await expect(page.getByText('QFS Node Network')).toBeVisible();
    });

    test('Wallet view loads', async ({ page }) => {
        await page.locator('button:has-text("Wallet")').first().click();
        await expect(page.locator('h2')).toContainText('wallet');
        // This confirms the Treasury hook is working and not throwing TypeError
        await expect(page.getByText(/Wallet Balance|Account/i).first()).toBeVisible();
    });

});
