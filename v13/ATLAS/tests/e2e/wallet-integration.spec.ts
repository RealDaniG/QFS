import { test, expect } from '@playwright/test';

test.describe('Wallet Integration', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');
    });

    test.skip('Connect Wallet button is visible and clickable', async ({ page }) => {
        // Trigger might be 'Connect Wallet' or an icon if not connected
        // Locate wrapper first
        const wrapper = page.getByTestId('wallet-connect-wrapper');
        await expect(wrapper).toBeVisible();

        // Find button within wrapper - RainbowKit might use different text depending on screen size or state
        // We look for any button inside the wrapper
        const connectBtn = wrapper.getByRole('button').first();
        await expect(connectBtn).toBeVisible();
        await connectBtn.click();

        // RainbowKit modal should appear
        // Note: actual connection requires MetaMask, so we just verify modal opens
        // RainbowKit usually uses a dialog or a specific portal
        // We look for role="dialog" or text "Connect a Wallet"
        await expect(page.getByText(/Connect a Wallet/i).or(page.locator('[role="dialog"]'))).toBeVisible({ timeout: 5000 });
    });

    test('Disconnected state shows correct UI', async ({ page }) => {
        // Verify "Not Connected" or address is NOT shown in sidebar logic
        // If sidebar shows "Not Connected" check that
        // OR check that we don't see an address like "0x..."

        // Check Auth Gate on Wallet Tab
        await page.goto('/?tab=wallet');
        await expect(page).toHaveURL(/.*tab=wallet/);
        await expect(page.getByText(/Wallet Connection Required/i)).toBeVisible();
    });

});
