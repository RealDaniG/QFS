# ATLAS v18 - Complete Verification & Enforcement Task List

**Date:** December 20, 2025  
**Discipline:** Implement → Restart → Verify → Log → Next  
**Status:** IN PROGRESS

---

## ✅ COMPLETED

### Step 0: API Verification Baseline

- [x] Test system health endpoint - ✅ WORKING
- [x] Test notifications endpoint - ✅ WORKING  
- [x] Test auth nonce endpoint - ✅ WORKING
- [x] Document verification results
- [x] Commit evidence

**Evidence:** API_VERIFICATION_COMPLETE.md

---

## 🔄 IN PROGRESS

### Step 1: Install Real Web3 Provider

- [ ] npm install wagmi viem @rainbow-me/rainbowkit - RUNNING
- [ ] Verify installation successful
- [ ] Restart dev server
- [ ] Test imports work

---

## 📋 CORE FUNCTIONALITY TASKS

### Step 2: Configure Real Wallet Connection

- [ ] Create wagmi config with mainnet/sepolia
- [ ] Wrap app in WagmiConfig + RainbowKitProvider
- [ ] Import RainbowKit CSS
- [ ] Replace WalletConnectButton with real ConnectButton
- [ ] **VERIFY:** Click "Connect Wallet" → MetaMask popup appears
- [ ] **VERIFY:** After connect → address shows in header
- [ ] **VERIFY:** No console errors
- [ ] Take screenshot as evidence
- [ ] Commit with verification

### Step 3: Wire Nonce/Sign/Verify Flow

- [ ] On wallet connect → fetch nonce from API
- [ ] Prompt wallet to sign nonce
- [ ] POST signature to /api/v18/auth/verify
- [ ] Store session token in useAuthStore
- [ ] Attach token to all API requests
- [ ] **VERIFY:** Network tab shows full flow
- [ ] **VERIFY:** Token stored and used
- [ ] **VERIFY:** No errors in console
- [ ] Document flow with screenshots
- [ ] Commit with verification

### Step 4: Add Route Guards

- [ ] Wrap Wallet view with auth check
- [ ] Wrap Bounties view with auth check
- [ ] Wrap Ledger view with auth check
- [ ] Wrap Messages view with auth check
- [ ] Wrap Settings view with auth check
- [ ] Remove mock reputation when !isConnected
- [ ] **VERIFY:** Unauthenticated → see gates, not data
- [ ] **VERIFY:** After auth → gates disappear
- [ ] **VERIFY:** No crashes
- [ ] Screenshot each view's gate
- [ ] Commit with verification

### Step 5: Wire Real Data to Components

- [ ] System Health → fetch from API every 10s
- [ ] Notifications → fetch from API, auto-refresh 30s
- [ ] Feed → fetch from /api/v18/content/feed
- [ ] Wallet Balance → fetch from API (create endpoint if needed)
- [ ] Communities → fetch from API (create endpoint if needed)
- [ ] **VERIFY:** Each component shows loading → data
- [ ] **VERIFY:** Empty states work
- [ ] **VERIFY:** Error states work
- [ ] **VERIFY:** No mock data displays
- [ ] Screenshot each component
- [ ] Commit with verification

### Step 6: Publishing Flow

- [ ] ContentComposer → block if !isConnected
- [ ] On publish → POST to /api/v18/content/publish
- [ ] Handle success → clear composer
- [ ] Handle error → show message
- [ ] Refresh feed after publish
- [ ] **VERIFY:** Publish works end-to-end
- [ ] **VERIFY:** Post appears in feed
- [ ] **VERIFY:** Errors handled gracefully
- [ ] Record video of flow
- [ ] Commit with verification

### Step 7: Per-View Manual Testing

- [ ] Test Home view (auth, feed, publish)
- [ ] Test Discover view (communities)
- [ ] Test Messages view (conversations)
- [ ] Test Wallet view (balance, history)
- [ ] Test Bounties view (list, actions)
- [ ] Test Ledger view (explain reward)
- [ ] Test Settings view (profile, guards)
- [ ] **VERIFY:** No crashes when clicking through
- [ ] **VERIFY:** All buttons work or show feedback
- [ ] Document results in table
- [ ] Commit with verification

### Step 8: Notification Bell

- [ ] Click bell → panel opens
- [ ] Fetch from API
- [ ] Auto-refresh every 30s
- [ ] **VERIFY:** Panel shows real data
- [ ] **VERIFY:** Refresh works
- [ ] **VERIFY:** No perpetual loading
- [ ] Screenshot panel
- [ ] Commit with verification

### Step 9: Playwright Tests

- [ ] Update tests for real wallet flow
- [ ] Test auth gates
- [ ] Test publishing
- [ ] Run full suite
- [ ] **VERIFY:** All tests pass
- [ ] **VERIFY:** No flakes
- [ ] Save test output
- [ ] Commit with verification

### Step 10: Orchestrator

- [ ] Run run_atlas_full.ps1
- [ ] **VERIFY:** All checks pass
- [ ] **VERIFY:** Logs complete
- [ ] Save logs
- [ ] Commit with verification

---

## 🔒 SECURITY & ENFORCEMENT TASKS

### A1: Auth Token Invalidation

- [ ] Create endpoint to test invalid tokens
- [ ] Tamper with token (change 1 character)
- [ ] Call protected endpoint with bad token
- [ ] **VERIFY:** Returns 401 Unauthorized
- [ ] **VERIFY:** No stack traces leaked
- [ ] **VERIFY:** Frontend clears session
- [ ] **VERIFY:** UI returns to auth gate
- [ ] Document test results
- [ ] Commit with verification

### A2: Wallet ↔ Session Binding

- [ ] Connect wallet A → authenticate
- [ ] Switch wallet in MetaMask (without refresh)
- [ ] Attempt API call
- [ ] **VERIFY:** Backend rejects mismatched address
- [ ] **VERIFY:** Frontend detects mismatch
- [ ] **VERIFY:** Forces re-auth
- [ ] Document test results
- [ ] Commit with verification

### A3: Nonce Replay Protection

- [ ] Fetch nonce
- [ ] Sign nonce
- [ ] Call /auth/verify twice with same nonce
- [ ] **VERIFY:** First call succeeds
- [ ] **VERIFY:** Second call returns 400/401
- [ ] **VERIFY:** Clear error message
- [ ] Document test results
- [ ] Commit with verification

---

## 🚨 FAILURE MODE VERIFICATION

### B1: Backend Down

- [ ] Stop backend
- [ ] Load frontend
- [ ] Navigate through all views
- [ ] **VERIFY:** Clear "Service unavailable" messages
- [ ] **VERIFY:** No infinite spinners
- [ ] **VERIFY:** No uncaught exceptions
- [ ] **VERIFY:** App remains usable
- [ ] Screenshot error states
- [ ] Commit with verification

### B2: Partial Failure

- [ ] Force notifications endpoint to return 500
- [ ] Keep other endpoints working
- [ ] **VERIFY:** Only notifications component errors
- [ ] **VERIFY:** Rest of app works
- [ ] **VERIFY:** No global crash
- [ ] Document behavior
- [ ] Commit with verification

---

## 🔗 IDENTITY BINDING ENFORCEMENT

### C1: GitHub Account Binding

- [ ] Create GitHub OAuth flow (or mock)
- [ ] Link GitHub account to wallet
- [ ] Attempt to link same GitHub to second wallet
- [ ] **VERIFY:** Backend rejects second link
- [ ] **VERIFY:** Clear error message
- [ ] Document enforcement
- [ ] Commit with verification

### C2: Commit Attribution

- [ ] Select known commit in repo
- [ ] Verify commit author → GitHub → wallet mapping
- [ ] Test commit with missing GitHub identity
- [ ] Test commit from unlinked account
- [ ] **VERIFY:** Only verified commits earn credit
- [ ] **VERIFY:** Past commits re-evaluated deterministically
- [ ] Document attribution logic
- [ ] Commit with verification

---

## 📊 VERSION & TRUTH ENFORCEMENT

### D1: Runtime Version Reporting

- [ ] Create /api/v18/system/version endpoint
- [ ] Return: api_version, commit, build_time, mock_pqc
- [ ] Display version in footer
- [ ] **VERIFY:** curl returns correct values
- [ ] **VERIFY:** Frontend shows version
- [ ] **VERIFY:** No ambiguity about runtime
- [ ] Document version info
- [ ] Commit with verification

### D2: Mock vs Real Crypto Flags

- [ ] Add MOCK_PQC flag to startup logs
- [ ] Add MOCK_LEDGER flag to startup logs
- [ ] Expose via /system/health
- [ ] **VERIFY:** Logs show crypto mode
- [ ] **VERIFY:** API exposes flags
- [ ] **VERIFY:** No hidden simulation
- [ ] Document crypto status
- [ ] Commit with verification

---

## 🏗️ CI & REPO HYGIENE

### E1: Verification Required PR Gate

- [ ] Add PR template requiring verification section
- [ ] Require curl output / screenshots
- [ ] Document enforcement policy
- [ ] **VERIFY:** Template exists
- [ ] **VERIFY:** Policy documented
- [ ] Commit template

### E2: API Documentation Tests

- [ ] Create test: every documented route exists
- [ ] Create test: every route returns non-404
- [ ] Add to CI pipeline
- [ ] **VERIFY:** Tests pass
- [ ] **VERIFY:** API drift caught
- [ ] Commit tests

---

## ✅ FINAL DEFINITION OF DONE

System is DONE when ALL of these are TRUE:

**Core Functionality:**

- [ ] Real wallet connection works (MetaMask popup)
- [ ] Auth flow (nonce → sign → verify → token) completes
- [ ] Route guards prevent unauthenticated access
- [ ] All core API routes return 2xx
- [ ] Publishing works; posts appear in feed
- [ ] All 7 views load without crashes
- [ ] Notification bell works with auto-refresh
- [ ] System health updates periodically
- [ ] No mock data unless labeled "Simulated"
- [ ] Orchestrator passes all checks

**Security & Enforcement:**

- [ ] Invalid tokens rejected with 401
- [ ] Wallet switching detected and forces re-auth
- [ ] Nonce replay protection works
- [ ] Backend down → graceful degradation
- [ ] Partial failures isolated
- [ ] GitHub ↔ wallet binding enforced
- [ ] Commit attribution verified

**Truth & Transparency:**

- [ ] Runtime version self-reported
- [ ] Mock vs real crypto flags exposed
- [ ] No hidden simulation modes
- [ ] API docs match reality

**Evidence:**

- [ ] Every claim backed by screenshot/curl output
- [ ] All verification results documented
- [ ] Test logs saved
- [ ] No "looks working" without proof

---

## 📊 PROGRESS TRACKING

**Completed:** 1/60+ tasks (API verification baseline)  
**In Progress:** 1 task (wagmi installation)  
**Remaining:** 58+ tasks

**Estimated Time:** 8-12 hours of focused work

---

## 🎯 CURRENT STATUS

**What's Verified Working:**

- ✅ API routes return proper JSON
- ✅ System health endpoint
- ✅ Notifications endpoint
- ✅ Auth nonce endpoint

**What's Next:**

1. Finish wagmi installation
2. Configure real wallet connection
3. Verify MetaMask popup appears
4. Wire nonce/sign/verify flow
5. Continue systematically through task list

**Operating Rule:**
> Every task ends with verification. No moving forward until current task is proven working with evidence.

---

**Last Updated:** December 20, 2025  
**Status:** Ready to continue with wagmi configuration
