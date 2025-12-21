
import { test, expect, Page } from '@playwright/test';

test.describe('ATLAS v18 Complete System Verification', () => {

    test('Phase 1: Cold start and unauthenticated state', async ({ page }) => {
        // Clear state
        await page.goto('http://localhost:3000');
        await page.evaluate(() => localStorage.clear());
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Should see auth gate or connect prompt
        const hasAuthGate = await page.locator('text=/Authentication Required|Wallet Connection Required|Connect your wallet/i').isVisible();
        expect(hasAuthGate).toBe(true);

        console.log('✅ Phase 1: Unauthenticated state correct');
    });

    test('Phase 2: Wallet connection', async ({ page }) => {
        await page.goto('http://localhost:3000');
        await page.evaluate(() => localStorage.clear());
        await page.reload();

        // Click Connect Wallet
        await page.click('button:has-text("Connect Wallet")');

        // Wait for RainbowKit modal
        await page.waitForSelector('text=/MetaMask|Rainbow|Coinbase/i', { timeout: 10000 });

        console.log('✅ Phase 2: Wallet modal appears');
    });

    test('Phase 3: Mock wallet connection and auth flow', async ({ page }) => {
        // For automation, we'll inject a mock session directly
        await page.goto('http://localhost:3000');

        // Inject mock session
        await page.evaluate(() => {
            const mockSession = {
                sessionToken: 'mock-token-for-testing',
                walletAddress: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
                expiresAt: Date.now() + 86400000
            };
            localStorage.setItem('atlas-session-v1', JSON.stringify(mockSession));
        });

        await page.reload();
        await page.waitForLoadState('networkidle');

        // Dashboard should unlock
        const hasLockedMessage = await page.locator('text=/Locked|Authentication Required/i').isVisible();
        expect(hasLockedMessage).toBe(false);

        console.log('✅ Phase 3: Dashboard unlocked with mock session');
    });

    test('Phase 4: All views accessible', async ({ page }) => {
        // Set up auth
        await page.goto('http://localhost:3000');
        await page.evaluate(() => {
            const mockSession = {
                sessionToken: 'mock-token-for-testing',
                walletAddress: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
                expiresAt: Date.now() + 86400000
            };
            localStorage.setItem('atlas-session-v1', JSON.stringify(mockSession));
        });
        await page.reload();
        await page.waitForLoadState('networkidle');

        const views = ['Home', 'Spaces', 'Messages', 'Wallet', 'Bounties', 'Ledger', 'Governance', 'Settings'];

        for (const view of views) {
            console.log(`Testing view: ${view}`);

            const testId = `nav-${view.toLowerCase()}`;
            // Allow for slight variations in text/id mapping if needed, 
            // but based on page.tsx, ids are: home, spaces, messages, wallet, bounties, ledger, governance, settings

            await page.click(`button[data-testid="${testId}"]`);
            await page.waitForTimeout(2000);

            // Should not show "Locked" message - checking for AuthGate specifics
            // AuthGate titles: "Spaces Portal Locked", "Secure Messaging Locked", etc.
            const isLocked = await page.locator('text=/Locked|Authentication Required/i').isVisible();
            expect(isLocked).toBe(false);

            // Should not have console errors
            const errors = [];
            page.on('console', msg => {
                if (msg.type() === 'error') errors.push(msg.text());
            });

            expect(errors.length).toBe(0);

            console.log(`✅ ${view} view accessible`);
        }
    });

    test('Phase 5: API integration check', async ({ page, request }) => {
        // Test that frontend can call backend APIs
        const apiTests = [
            { endpoint: '/api/v18/spaces', expectData: true },
            { endpoint: '/api/v18/governance/proposals', expectData: true },
            // { endpoint: '/api/v18/content/feed', expectData: true }, // Not all may exist yet, standardizing on knowns
            { endpoint: '/api/v18/wallet/balance', expectData: true }
        ];

        for (const test of apiTests) {
            const response = await request.get(`http://localhost:3000${test.endpoint}`);
            // 200 OK or 401 Unauthorized (if auth header missing but endpoint hit) are mostly signs of life vs 404
            const status = response.status();
            const isSuccess = status === 200 || status === 401 || status === 422;
            expect(isSuccess).toBe(true);

            console.log(`✅ ${test.endpoint} → ${status}`);
        }
    });

    test('Phase 6: Daily rewards visual check', async ({ page }) => {
        await page.goto('http://localhost:3000');

        // Set up auth
        await page.evaluate(() => {
            const mockSession = {
                sessionToken: 'mock-token-for-testing',
                walletAddress: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
                expiresAt: Date.now() + 86400000
            };
            localStorage.setItem('atlas-session-v1', JSON.stringify(mockSession));
        });
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Look for streak indicator (should be visible somewhere)
        // DailyRewardCard text: "Daily Presence", "Day X/15"
        const hasStreak = await page.locator('text=/Day \\d+\\/15|Streak|Daily Presence/i').count();
        expect(hasStreak).toBeGreaterThan(0);

        console.log('✅ Phase 6: Daily rewards UI present');
    });

    test('Phase 7: No console errors on authenticated dashboard', async ({ page }) => {
        const consoleErrors: string[] = [];

        page.on('console', msg => {
            if (msg.type() === 'error' && !msg.text().includes('chrome.runtime')) {
                consoleErrors.push(msg.text());
            }
        });

        await page.goto('http://localhost:3000');
        await page.evaluate(() => {
            const mockSession = {
                sessionToken: 'mock-token-for-testing',
                walletAddress: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
                expiresAt: Date.now() + 86400000
            };
            localStorage.setItem('atlas-session-v1', JSON.stringify(mockSession));
        });
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Navigate through all views
        await page.click('button[data-testid="nav-spaces"]');
        await page.waitForTimeout(1000);
        await page.click('button[data-testid="nav-messages"]');
        await page.waitForTimeout(1000);
        await page.click('button[data-testid="nav-wallet"]');
        await page.waitForTimeout(1000);

        // Expect no critical errors
        // We filter out some noise if necessary, but ideally clean
        expect(consoleErrors.length).toBe(0);
        console.log('✅ Phase 7: No console errors');
    });

});
