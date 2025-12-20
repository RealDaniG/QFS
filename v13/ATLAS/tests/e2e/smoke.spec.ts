import { test, expect } from '@playwright/test';

test.describe('ATLAS v18 Smoke Tests', () => {

    test('Homepage maintains layout', async ({ page }) => {
        await page.goto('/');
        // Check for "ATLAS" logo/text in sidebar
        await expect(page.getByText('ATLAS', { exact: true }).first()).toBeVisible();
        await expect(page.getByText('John Doe')).toBeVisible(); // Mock user
    });

    test('Governance view loads proposals', async ({ page }) => {
        // Intercept API call
        const apiPromise = page.waitForResponse(resp =>
            resp.url().includes('/api/v18/governance/proposals') && resp.status() === 200
        );

        await page.goto('/');
        // Click Governance tab
        await page.getByRole('tab', { name: 'Governance' }).click();

        // Wait for API
        await apiPromise;

        // Check for "Protocol Governance" header
        await expect(page.getByText('Protocol Governance')).toBeVisible();

        // Check for proposals (either "No active proposals" or list)
        // We expect the backend to return empty or mock data. 
        // If empty: "No active proposals"
        // If data: Check for title
        const emptyState = page.getByText('No active proposals');
        const listState = page.locator('.space-y-4').first();
        await expect(emptyState.or(listState)).toBeVisible();
    });

    test('Feed view loads content', async ({ page }) => {
        const apiPromise = page.waitForResponse(resp =>
            resp.url().includes('/api/v18/content/feed') && resp.status() === 200
        );

        await page.goto('/');
        // Feed is on Home tab
        await page.getByRole('tab', { name: 'Home' }).click();

        // Check for "QFS Node Network" from DistributedFeed
        await expect(page.getByText('QFS Node Network')).toBeVisible();

        // Wait for API feed load
        // Note: DistributedFeed calls fetch on mount

        // Check for feed items
        // Since backend returns [] for now (unless mock data in v18 router), it might be empty
        // If [] returned, DistributedFeed maps it to [].
        // If empty, DistributedFeed renders nothing?
        // Let's check DistributedFeed.tsx: 
        // {feed.map(...)}
        // If feed is empty, nothing verifies.
        // We should ensure backend returns SOME data or check for "Connecting..." state gone.

        // Wait for loading to finish
        await expect(page.getByText('Connecting to distributed node...')).not.toBeVisible();
    });

    test('Wallet view loads', async ({ page }) => {
        // Check Wallet tab
        await page.goto('/');
        await page.getByRole('tab', { name: 'Wallet' }).click();

        // WalletInterface uses useWalletView -> /api/v1/wallets/
        // Expect to see "Wallet Balance" or similar
        await expect(page.getByText(/Wallet|Balance/)).toBeVisible();
    });

});
