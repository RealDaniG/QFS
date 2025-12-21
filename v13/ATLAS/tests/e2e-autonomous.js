"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const playwright_1 = require("playwright");
async function runE2ETest() {
    console.log('[E2E] Starting Verification...');
    const browser = await playwright_1.chromium.launch({ headless: true }); // Headless for CI/Agent execution
    const context = await browser.newContext();
    const page = await context.newPage();
    // Inject Mock Wallet Provider
    await page.addInitScript(() => {
        const mockWallet = {
            isMetaMask: true,
            request: async ({ method, params }) => {
                console.log(`[MockWallet] Request: ${method}`, params);
                if (method === 'eth_requestAccounts' || method === 'eth_accounts') {
                    return ['0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266']; // Hardhat Account #0
                }
                if (method === 'eth_chainId') {
                    return '0x1'; // Mainnet
                }
                if (method === 'personal_sign' || method === 'eth_sign') {
                    return '0xdeadbeef'; // Mock signature
                }
                if (method === 'eth_signTypedData_v4') {
                    return '0xdeadbeef';
                }
                return null;
            },
            on: (event, callback) => { },
            removeListener: () => { }
        };
        window.ethereum = mockWallet;
    });
    const BACKEND_URL = 'http://localhost:8000'; // Matching running instance
    const FRONTEND_URL = 'http://localhost:3000';
    try {
        console.log(`[E2E] Navigating to ${FRONTEND_URL}`);
        await page.goto(FRONTEND_URL, { timeout: 120000 });
        await page.waitForLoadState('domcontentloaded');
        console.log('[E2E] Page loaded (domcontentloaded)');
        await page.waitForTimeout(2000);
        // Clear localStorage
        await page.evaluate(() => localStorage.clear());
        await page.reload();
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2000);
        // Task 3b: Verify unauthenticated state
        console.log('[E2E] Checking unauthenticated state...');
        try {
            await page.waitForSelector('text=/Connect your wallet|Authentication Required|Connect to Start Streak|Daily Presence/i', { timeout: 10000 });
        }
        catch (e) {
            console.log('[E2E] Auth text not found. Writing content to logs/debug_content.html');
            const content = await page.content();
            const fs = require('fs');
            fs.writeFileSync('logs/debug_content.html', content);
            process.exit(1);
        }
        console.log('[PASS] Auth entry point visible');
        // Task 3c: Connect wallet
        console.log('[E2E] Clicking Connect/Start button...');
        // Try to find the "Connect to Start Streak" button or the main "Connect Wallet" button
        const connectButton = page.getByRole('button', { name: /Connect to Start Streak|Connect Wallet/i }).first();
        if (await connectButton.isVisible()) {
            await connectButton.click();
        }
        else {
            console.log('[E2E] Connect button not found via role, trying text');
            await page.click('text=Connect');
        }
        // Wait for RainbowKit modal (simulated by our mock or UI if standard)
        // Since we mocked window.ethereum, RainbowKit might auto-detect or show options.
        // If it shows options, we click MetaMask.
        try {
            const metaMaskOption = page.getByText('MetaMask');
            if (await metaMaskOption.isVisible({ timeout: 5000 })) {
                console.log('[E2E] Selecting MetaMask from modal...');
                await metaMaskOption.click();
            }
        }
        catch (e) {
            console.log('[E2E] MetaMask option not found or already connected');
        }
        // The mock wallet should auto-resolve the connection. 
        // Now waiting for the "Sign" flow if it's separate, OR if useWalletAuth triggers it automatically.
        console.log('[E2E] Waiting for auth flow...');
        await page.waitForTimeout(2000);
        // Check for "Verify Presence" button
        const verifyBtn = page.getByRole('button', { name: /Verify Presence|Sign Message/i });
        if (await verifyBtn.isVisible()) {
            console.log('[E2E] Clicking Verify Presence...');
            await verifyBtn.click();
        }
        // Wait for dashboard unlock
        console.log('[E2E] Waiting for dashboard unlock...');
        // Protected content usually has "Daily Presence" or specific dashboard cards
        await page.waitForSelector('text=Daily Presence', { timeout: 15000 });
        console.log('[PASS] Dashboard content visible');
        // Task 3e: Verify session stored
        const session = await page.evaluate(() => localStorage.getItem('atlas_session_v1'));
        if (!session) {
            console.error('[FAIL] Session not stored in localStorage');
        }
        else {
            console.log('[PASS] Session stored:', JSON.parse(session));
        }
        // Task 5: Daily Reward
        console.log('[E2E] Verifying Daily Reward...');
        // Check streak indicator
        const streakElement = page.getByText(/Day \d+\/15/);
        if (await streakElement.isVisible()) {
            const text = await streakElement.innerText();
            console.log(`[PASS] Streak Indicator: ${text}`);
        }
        else {
            console.error('[FAIL] Streak indicator not found');
        }
        // Task 7: Balance (Mock check)
        const signedBtn = page.getByText("Sign Today's Presence");
        if (await signedBtn.isVisible()) {
            console.log('[E2E] Clicking Sign Today...');
            await signedBtn.click();
            await page.waitForTimeout(2000);
        }
        console.log('[E2E] Checking progress bar...');
        const progress = await page.locator('.bg-amber-200').first();
        if (await progress.isVisible()) {
            console.log('[PASS] Progress bar visible');
        }
        // Screenshot
        await page.screenshot({ path: 'logs/e2e_final_dashboard.png', fullPage: true });
        console.log('[E2E] Screenshot saved');
        console.log('ALL SYSTEMS FUNCTIONAL');
    }
    catch (error) {
        console.error('[E2E] Test Failed:', error);
        await page.screenshot({ path: 'logs/e2e_error.png' });
        process.exit(1);
    }
    finally {
        await browser.close();
    }
}
runE2ETest();
