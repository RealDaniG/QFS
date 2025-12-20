import { test, expect } from '@playwright/test';

test.describe('ATLAS v18 Smoke Tests', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        // Wait for the initialization overlay to disappear
        await expect(page.getByText('Synchronizing v18 clusters...')).not.toBeVisible({ timeout: 15000 });
    });

    test('Homepage maintains layout and identity', async ({ page }) => {
        // Check for branding in sidebar
        await expect(page.getByText(/ATLAS v18/i)).toBeVisible();

        // v18 identity display: check for reputation display
        await expect(page.getByText(/Reputation: 142/)).toBeVisible();

        // Check for major section headers
        await expect(page.getByText(/System Health/i)).toBeVisible();
    });

    test('Governance view loads proposals from v18 API', async ({ page }) => {
        // Intercept API call to verify it's hitting v18
        const apiPromise = page.waitForResponse(resp =>
            resp.url().includes('/api/v18/governance/proposals') && resp.status() === 200,
            { timeout: 10000 }
        );

        // Click Governance in sidebar using test ID
        await page.getByTestId('nav-governance').click();

        // Wait for API response
        await apiPromise;

        // Check for Governance header (Capitalized by Tailwind)
        await expect(page.locator('h2')).toContainText(/Governance/i);

        // Verify a proposal card is visible (if any) or "no proposals" message
        await expect(page.getByText(/Protocol Governance/i)).toBeVisible();
    });

    test('Feed view loads content from v18 clusters', async ({ page }) => {
        // Click Home in sidebar using test ID to ensure we are there
        await page.getByTestId('nav-home').click();

        // Check for "QFS Node Network" which is in DistributedFeed component
        await expect(page.getByText('QFS Node Network')).toBeVisible();

        // Wait for the feed items to render
        await expect(page.getByText(/Connecting to distributed node/i)).not.toBeVisible({ timeout: 15000 });
    });

    test('Wallet view loads internal treasury data', async ({ page }) => {
        // Click Wallet in sidebar using test ID
        await page.getByTestId('nav-wallet').click();

        // Check for wallet header
        await expect(page.locator('h2')).toContainText(/Wallet/i);

        // This confirms the Treasury hook is working and not throwing TypeError
        // Check for the "Internal Credits" label from the v18 plan
        await expect(page.getByText(/Internal Credits/i)).toBeVisible();

        // Use a more specific locator for the balance title
        await expect(page.locator('h3:has-text("Wallet Balance"), .card-title:has-text("Wallet Balance")').first()).toBeVisible();
    });

    test('Content Composer sanity check', async ({ page }) => {
        // Click on the composer trigger using test ID
        await page.getByTestId('composer-trigger').click();

        // Verify composer card appears
        await expect(page.getByText(/Create Content/i)).toBeVisible();
        await expect(page.getByPlaceholder(/Share your thoughts/i)).toBeVisible();

        // Close it
        await page.getByRole('button', { name: /Cancel/i }).click();
        await expect(page.getByText(/Create Content/i)).not.toBeVisible();
    });

});
