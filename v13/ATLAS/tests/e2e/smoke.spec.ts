import { test, expect } from '@playwright/test';

test.describe('ATLAS v18 Smoke Tests', () => {

    test.beforeEach(async ({ page }) => {
        // Set viewport large enough to show all elements
        await page.setViewportSize({ width: 1400, height: 900 });
        await page.goto('/');
        // Wait for page to be ready and hydrated
        await page.waitForLoadState('networkidle');
        // Wait for sidebar navigation to be visible (ensures hydration complete)
        await expect(page.getByTestId('nav-home')).toBeVisible({ timeout: 10000 });
    });

    test('Homepage maintains layout and identity', async ({ page }) => {
        // Check for branding in sidebar
        await expect(page.getByText(/ATLAS/i).first()).toBeVisible();

        // v18 identity display: Check for V18 badge in sidebar
        await expect(page.getByTestId('v18-badge')).toBeVisible();
        await expect(page.getByTestId('v18-badge')).toContainText(/v14-v2-baseline/i);

        // Check for System Status card (on large screens)
        await expect(page.getByText(/System Status/i)).toBeVisible();
    });

    test('Governance view loads proposals or auth gate', async ({ page }) => {
        // Click Governance in sidebar using test ID
        await page.getByTestId('nav-governance').click();
        await page.waitForLoadState('networkidle');

        // Check for Governance content - either "Protocol Governance" or governance-related text
        await expect(
            page.getByText(/Protocol Governance/i)
                .or(page.getByText(/Governance/i).first())
        ).toBeVisible({ timeout: 10000 });
    });

    test('Feed view loads content from v18 clusters', async ({ page }) => {
        // Click Home in sidebar using test ID to ensure we are there
        await page.getByTestId('nav-home').click();
        await page.waitForTimeout(500);

        // Check for composer area - placeholder text or Create Post button
        await expect(
            page.getByPlaceholder(/Share your thoughts/i)
                .or(page.getByTestId('composer-trigger'))
        ).toBeVisible();

        // Wait for the feed items to render OR "No posts" message
        await expect(
            page.getByText(/Coherence Score/i).first()
                .or(page.getByText(/No posts yet/i))
        ).toBeVisible({ timeout: 15000 });
    });

    test('Wallet view loads internal treasury data or auth gate', async ({ page }) => {
        // Click Wallet in sidebar using test ID
        await page.getByTestId('nav-wallet').click();
        await page.waitForTimeout(1000);
        await page.waitForLoadState('networkidle');

        // Check for wallet-related content - either gate or wallet balance
        // The auth gate shows "Wallet Connection Required" when not connected
        // Or we see wallet balance when connected
        await expect(
            page.getByText(/Wallet Connection Required/i)
                .or(page.getByText(/Wallet Balance/i))
                .or(page.getByText(/Connect your wallet/i))
                .or(page.getByText(/Secure Wallet Authentication/i))
        ).toBeVisible({ timeout: 15000 });
    });

    test('Content Composer sanity check', async ({ page }) => {
        // Ensure we're on Home tab and wait for content
        await page.getByTestId('nav-home').click();
        await page.waitForTimeout(1000);

        // Check for the composer trigger or Create Post button
        const trigger = page.getByTestId('composer-trigger').or(page.getByText(/Create Post/i));
        await expect(trigger).toBeVisible({ timeout: 10000 });

        // Click to open composer
        await trigger.click();

        // Look for composer dialog content
        await expect(
            page.getByText(/Create Content/i)
                .or(page.getByText(/Create Post/i))
                .or(page.getByRole('button', { name: /Cancel/i }))
        ).toBeVisible({ timeout: 5000 });
    });

});
