import { test, expect } from '@playwright/test';

test.describe('ATLAS v18 Smoke Tests', () => {

    test.use({ viewport: { width: 1280, height: 720 } });

    test.beforeEach(async ({ page }) => {
        // Go to home page
        await page.goto('/');
        // Wait for network idle to ensure initial chunks are loaded
        await page.waitForLoadState('networkidle');
    });

    test('Homepage maintains layout and identity', async ({ page }) => {
        // Assert URL (implicitly 'home' default)
        // Check for ATLAS logo/text
        await expect(page.getByText(/ATLAS/i).first()).toBeVisible();

        // Check for sidebar navigation elements
        await expect(page.getByTestId('nav-home')).toBeVisible();
        await expect(page.getByTestId('nav-governance')).toBeVisible();
        await expect(page.getByTestId('nav-wallet')).toBeVisible();

        // Check v18 badge (Phase D)
        await expect(page.getByTestId('v18-badge')).toBeVisible();
    });

    test('Governance navigation updates URL and renders content', async ({ page }) => {
        // Click Governance in sidebar
        await page.getByTestId('nav-governance').click();

        // Phase H: Assert URL
        await expect(page).toHaveURL(/.*tab=governance/);

        // Check for governance-related content or loading state dissapearance
        // (Assuming data might load)
        await expect(page.getByText(/Protocol Governance/i)).toBeVisible();
    });

    test('Wallet navigation updates URL and renders auth gate', async ({ page }) => {
        // Click Wallet
        await page.getByTestId('nav-wallet').click();

        // Phase H: Assert URL
        await expect(page).toHaveURL(/.*tab=wallet/);

        // Phase D: Exact heading check
        await expect(page.getByRole('heading', { name: 'Wallet Connection Required' })).toBeVisible();
    });

    test.skip('Feed view loads content', async ({ page }) => {
        // Ensure Home (default)
        if (page.url().includes('tab=')) {
            await page.getByTestId('nav-home').click();
        }

        // Wait for loading state to disappear
        await page.waitForSelector('[data-testid="feed-loading"]', { state: 'hidden', timeout: 15000 }).catch(() => { });

        // Wait for the feed items to render OR "No posts" message
        await expect(
            page.getByTestId('feed-item').first()
                .or(page.getByTestId('feed-empty'))
        ).toBeVisible({ timeout: 15000 });
    });

    test.skip('Content Composer sanity check', async ({ page }) => {
        // Ensure Home
        await page.goto('/?tab=home');

        // Check for the composer trigger
        const trigger = page.getByTestId('composer-trigger').or(page.getByText(/Create Post/i));
        await expect(trigger.first()).toBeVisible();

        // Click to open composer
        await trigger.first().click();

        // Check if modal/dialog appears (using TestId which propagates to the role=dialog div)
        await expect(page.getByTestId('composer-dialog')).toBeVisible();

        // Check for text area
        await expect(page.getByRole('textbox')).toBeVisible();
    });

});
