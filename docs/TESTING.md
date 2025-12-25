# TESTING.md — ATLAS v18 Verification Guide

This guide covers automated and manual testing procedures for the v18 Distributed Dashboard.

## 🧪 Automated Testing

### 1. Full System Verification (Orchestrator)

Run the automated suite to check backend, frontend, and API integrity:

```powershell
powershell -ExecutionPolicy Bypass -File run_atlas_full.ps1
```

### 2. UI Smoke Tests (Playwright)

```bash
cd v13/atlas
npm run test:e2e
```

---

## 🧪 Manual Wallet Connection Test

1. Ensure MetaMask extension is installed and unlocked in your browser.
2. Open `http://localhost:3000`.
3. Click **"Connect Wallet"** in the top-right corner.
4. RainbowKit modal should appear with **MetaMask** as a selectable option.
5. Click **MetaMask** → approve the connection request in the extension popup.
6. Verify your wallet address (e.g., `0x123...`) appears in the sidebar footer.
7. Observe the **"Unverified Session"** transition to **"Reputation: 142"** (after cryptographic verification).
8. Check browser console (F12) to ensure no `401` or `500` errors on `/api/v18/auth/*` calls.

---

## 🧪 Auth Gate Verification

1. Navigate to **Home** (connected but potentially unverified).
2. Click **"Wallet"** or **"Messages"** in the sidebar.
3. If not signed in (cryptographically), an **"AuthGate"** modal/view should block access.
4. Verify access is granted to the protected view.

---

## 🧪 Auth & Zero-Sim Verification

### 1. Golden Trace Replay

Verify that the entire authentication lifecycle is deterministic and replayable:

```powershell
python tests/replay/auth_golden_trace.py
```

**Success Criteria:**

- Output MUST be identical to `tests/artifacts/auth_golden_trace.json`.
- No drift in `session_id` generation or Event IDs.

### 2. Device Binding Check

Verify device hash stability:

```powershell
python scripts/verify_device_identity.py
```
