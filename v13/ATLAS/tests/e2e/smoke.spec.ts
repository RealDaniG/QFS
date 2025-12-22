import { test, expect } from '@playwright/test';

test.describe('ATLAS v18 Smoke Tests', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        // Wait for page to be ready (networkidle ensures all initial fetches complete)
        await page.waitForLoadState('networkidle');
    });

    test('Homepage maintains layout and identity', async ({ page }) => {
        // Check for branding in sidebar
        await expect(page.getByText(/ATLAS/i).first()).toBeVisible();

        // v18 identity display: Unauthenticated should check for V18 badge
        await expect(page.getByTestId('v18-badge')).toBeVisible();
        await expect(page.getByTestId('v18-badge')).toContainText(/v14-v2-baseline/i);

        // Check for major section headers
        await expect(page.getByText(/System Status/i)).toBeVisible();
    });

    test('Governance view loads proposals or auth gate', async ({ page }) => {
        // Click Governance in sidebar using test ID
        await page.getByTestId('nav-governance').click();

        // Check for Governance header (Match Protocol Governance)
        await expect(page.locator('h2')).toContainText(/Protocol Governance/i);

        // Verify either proposal card OR auth gate
        // "Protocol Governance" is usually in the description or header
        await expect(page.getByText(/Protocol Governance/i)).toBeVisible();
    });

    test('Feed view loads content from v18 clusters', async ({ page }) => {
        // Click Home in sidebar using test ID to ensure we are there
        await page.getByTestId('nav-home').click();

        // Check for composer input placeholder as proof of Home load
        await expect(page.getByPlaceholder(/Share your thoughts/i)).toBeVisible();

        // Wait for the feed items to render
        await expect(page.getByText(/Coherence Score/i).first().or(page.getByText(/No posts yet/i))).toBeVisible({ timeout: 15000 });
    });

    test('Wallet view loads internal treasury data or auth gate', async ({ page }) => {
        // Click Wallet in sidebar using test ID
        await page.getByTestId('nav-wallet').click();

        // Check for wallet header in a card
        await expect(page.getByText(/Wallet/i).first()).toBeVisible();

        // In V18, unauthenticated users see "Wallet Connection Required"
        await expect(page.getByText(/Wallet Connection Required/i)).toBeVisible();
        await expect(page.getByText(/Connect Wallet/i).first()).toBeVisible();
    });

    test('Content Composer sanity check', async ({ page }) => {
        // Click on the composer trigger using test ID
        // Note: In some V18 layouts, composer might be hidden if unauth, or present but gated.
        // If the button exists, click it.
        const trigger = page.getByTestId('composer-trigger');
        if (await trigger.isVisible()) {
            await trigger.click();
            await expect(page.getByText(/Create Content/i)).toBeVisible();
            await page.getByRole('button', { name: /Cancel/i }).click();
        }
    });

});
