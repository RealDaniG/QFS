# v18 Alpha Manual Test Results

**Tester:** [Your Name]
**Date:** [YYYY-MM-DD]
**Build:** v18-alpha (Release Candidate 1)

## 🎯 Verification Checklist

### Tier 1: Critical Blockers (Must Pass)

- [x] **Backend Startup**: `atlas_launch.bat` starts 3-node cluster (A, B, C) without crash. - *Verified: Service running on port 8001*
- [ ] **App Launch**: `ATLAS v18 Beta.exe` launches and connects to backend (Network Status: Green).
- [ ] **Wallet Connection**:
  - [ ] Clicking "Connect Wallet" opens RainbowKit modal.
  - [ ] Can scan QR code OR connect MetaMask extension.
  - [ ] Wallet address appears in sidebar after connection.
- [ ] **Navigation**:
  - [ ] "Governance" tab loads.
  - [ ] "Wallet" tab loads.
  - [ ] "Market" tab loads.
- [ ] **Content**:
  - [ ] Feed loads (shows posts or "No posts").
  - [ ] Content Composer dialog opens.

### Tier 2: Stability & UX

- [ ] **Persistence**: Wallet stays connected after closing and reopening app.
- [ ] **Error Handling**: Disconnecting network shows "Offline" status (doesn't crash).
- [ ] **Security**: Windows SmartScreen warning appears (expected for unsigned/Alpha).

## 📝 Notes & Issues

### Issue 1: [Short Description]

- **Severity**: Critical / High / Low
- **Steps**:
  1. ...
- **Expected**: ...
- **Actual**: ...

### Issue 2: [Short Description]

- ...
