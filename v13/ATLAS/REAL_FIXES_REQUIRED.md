# ATLAS v18 - REAL FIXES REQUIRED

**Date:** December 20, 2025  
**Status:** CRITICAL - MOCK DATA MUST BE REPLACED  
**Priority:** P0 - IMMEDIATE ACTION REQUIRED

---

## 🚨 CURRENT REALITY CHECK

You are correct. Despite creating API routes:

1. **System Health** - Shows "Loading..." because API route exists but Next.js hasn't rebuilt
2. **Wallet Connection** - Still mock because we need REAL Web3 provider
3. **Notifications** - API exists but needs server restart to work

**ROOT CAUSE:** I was creating infrastructure without ensuring it actually works.

---

## ✅ IMMEDIATE FIXES (Next 30 Minutes)

### Fix 1: Restart Dev Server to Pick Up API Routes

```bash
# Stop current dev server
# Restart to rebuild with new API routes
npm run dev
```

### Fix 2: Verify API Routes Actually Work

```bash
# Test system health endpoint
curl http://localhost:3000/api/v18/system/health

# Test notifications endpoint  
curl http://localhost:3000/api/v18/notifications

# Should return JSON, not 404
```

### Fix 3: Install REAL Web3 Provider (wagmi for EVM)

```bash
npm install wagmi viem @tanstack/react-query
npm install @rainbow-me/rainbowkit
```

### Fix 4: Configure Real Wallet Connection

Create `src/app/providers.tsx` with actual wagmi config:

```typescript
'use client';

import { WagmiConfig, createConfig, configureChains } from 'wagmi';
import { mainnet, polygon } from 'wagmi/chains';
import { publicProvider } from 'wagmi/providers/public';
import { RainbowKitProvider, getDefaultWallets } from '@rainbow-me/rainbowkit';
import '@rainbow-me/rainbowkit/styles.css';

const { chains, publicClient } = configureChains(
  [mainnet, polygon],
  [publicProvider()]
);

const { connectors } = getDefaultWallets({
  appName: 'ATLAS v18',
  projectId: 'YOUR_PROJECT_ID', // Get from WalletConnect
  chains
});

const wagmiConfig = createConfig({
  autoConnect: true,
  connectors,
  publicClient
});

export function Web3Provider({ children }: { children: React.ReactNode }) {
  return (
    <WagmiConfig config={wagmiConfig}>
      <RainbowKitProvider chains={chains}>
        {children}
      </RainbowKitProvider>
    </WagmiConfig>
  );
}
```

---

## 📋 COMPREHENSIVE TASK LIST (From Your Prompt)

### Task 0: Logo & Branding ✅ DONE

- [x] Logo image replaced (alien saucer)
- [ ] TODO: Add Montserrat Bold font
- [ ] TODO: Add gradient styling
- [ ] TODO: Integrate v18 badge into logo

### Task 1: Real Authentication

- [ ] Install wagmi + rainbowkit
- [ ] Wrap app in Web3Provider
- [ ] Replace useWalletAuth with real wagmi hooks
- [ ] Implement real nonce/sign/verify flow
- [ ] Add route guards to all protected views
- [ ] Remove mock reputation when unauthenticated

### Task 2: Backend API Wiring

- [ ] Profile API - Fix store.save error
- [ ] Content Publishing API - Wire to real backend
- [ ] Wallet/Treasury API - Real FLX balance
- [ ] Bounties API - Real bounty data
- [ ] Guards API - Real guard list
- [ ] Messages API - Real conversations
- [ ] Communities API - Real community data
- [ ] Search API - Wire header search
- [ ] Explain Reward API - Fix errors

### Task 3: Remove Mock Data

- [ ] Reputation - Only show when authenticated
- [ ] FLX Balance - From API only
- [ ] Communities - From API or "Coming Soon"
- [ ] Messages - From API or empty state
- [ ] Notifications - From API with refresh
- [ ] System Health - From API or labeled "Demo"

### Task 4: Publishing Flow

- [ ] ContentComposer auth check
- [ ] POST to /api/v18/content/publish
- [ ] Handle success/error
- [ ] Refresh feed after publish
- [ ] DistributedFeed from real API
- [ ] Empty state handling

### Task 5: Per-View Validation

- [ ] Home - Auth banner, real feed, publishing works
- [ ] Discover - Real communities or "Coming Soon"
- [ ] Messages - Real conversations or empty
- [ ] Wallet - Real balance, requires auth
- [ ] Bounties - Real data or "Coming Soon"
- [ ] Ledger & Explain - Working explain endpoint
- [ ] Settings - Profile saves, guards load

### Task 6: Notification Bell

- [ ] Click opens panel
- [ ] Fetches from API
- [ ] Auto-refresh every 30s
- [ ] Real notifications or labeled

### Task 7: System Health

- [ ] Poll /api/v18/system/health every 10s
- [ ] Update badges in real-time
- [ ] Or label as "Simulated"

### Task 8: Browser Audit

- [ ] Test every button
- [ ] Test every view
- [ ] Document all failures
- [ ] Fix all crashes

### Task 9: Playwright Tests

- [ ] Update for real wallet flow
- [ ] Test auth gates
- [ ] Test publishing
- [ ] All tests pass

### Task 10: Orchestrator

- [ ] run_atlas_full.ps1 works
- [ ] All checks pass
- [ ] Logs complete

---

## 🎯 DEFINITION OF DONE

System is DONE when:

1. **Wallet Connection**
   - Clicking "Connect Wallet" opens MetaMask
   - User signs message
   - Session created
   - Address shown in header
   - Reputation shown in sidebar

2. **All Views Work**
   - No crashes when clicking through
   - Real data or clear "Coming Soon" labels
   - No perpetual loading states

3. **Publishing Works**
   - Can create post
   - Post appears in feed
   - No errors

4. **All APIs Respond**
   - No 404s
   - No timeouts
   - Real data or clear errors

5. **Tests Pass**
   - Playwright suite green
   - Backend tests pass
   - No console errors

---

## 🚀 IMMEDIATE ACTION PLAN

**Right Now (Next 10 minutes):**

1. Restart dev server to pick up API routes
2. Test API routes with curl
3. Verify system health loads
4. Verify notifications load

**Next (30 minutes):**
5. Install wagmi + rainbowkit
6. Configure real Web3 provider
7. Test real wallet connection

**Then (1 hour):**
8. Fix backend endpoints one by one
9. Remove all mock data
10. Test each view thoroughly

**Finally (2 hours):**
11. Run full browser audit
12. Update Playwright tests
13. Run orchestrator
14. Document completion

---

**STATUS:** Ready to implement REAL fixes. No more mock data. No more "it should work". Only verified, working functionality.
