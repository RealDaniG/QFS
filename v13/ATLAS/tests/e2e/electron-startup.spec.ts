import { _electron as electron, test, expect } from '@playwright/test';
import path from 'path';

test('Electron app startup and wallet button check', async () => {
    // Launch Electron app from source
    // We point to the 'desktop' folder which contains package.json with "main": "main.js"
    const electronApp = await electron.launch({
        args: [path.join(__dirname, '../../desktop/')],
        env: { ...process.env, NODE_ENV: 'development', SKIP_BACKEND: 'true' }
    });

    try {
        const window = await electronApp.firstWindow();

        // Verify title
        console.log('Window Title:', await window.title());

        // Wait for Shell to load
        const walletWrapper = window.locator('[data-testid="wallet-connect-wrapper"]');
        await expect(walletWrapper).toBeVisible({ timeout: 20000 });

        // Check Connect Button
        const connectBtn = walletWrapper.getByRole('button', { name: /connect/i }).first();
        await expect(connectBtn).toBeVisible();
        await expect(connectBtn).toBeEnabled();

        // Click it to see if modal triggers
        await connectBtn.click();

        // Check for RainbowKit modal
        // RainbowKit modals usually have role="dialog"
        const modal = window.locator('div[role="dialog"]');
        await expect(modal).toBeVisible({ timeout: 10000 });

        console.log('Wallet modal opened successfully');

    } finally {
        await electronApp.close();
    }
});
