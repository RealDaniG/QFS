# ATLAS v18 Final Verification Checklist

**Target:** Production-ready Electron + Web deployment
**Due:** December 23, 2025

## ✅ Already Verified (from commits)

- [x] URL-based navigation working (PR #29)
- [x] E2E tests: Homepage, Governance, Wallet tabs
- [x] Backend auth endpoints functional
- [x] CORS fixed (127.0.0.1:8001)
- [x] Static imports (no hydration issues)
- [x] Launcher with test/cleanup modes

## 🔄 Phase 2: Electron Wallet Integration

### 2.1 Desktop App Launch

- [ ] `npm run electron:dev` starts without errors
- [ ] Console shows no CSP violations
- [ ] Main window loads `http://localhost:3000`

### 2.2 Wallet Connection

- [ ] "Connect Wallet" button visible in header
- [ ] Click triggers RainbowKit modal
- [ ] MetaMask option appears in modal
- [ ] MetaMask browser extension detected (if installed)
- [ ] Connection request sent to MetaMask
- [ ] User approves connection
- [ ] Wallet address appears in sidebar
- [ ] Session persists on page reload

### 2.3 Authenticated Features

- [ ] Navigate to Wallet tab → shows internal credits
- [ ] Navigate to Governance → can view proposals
- [ ] Click "Create Post" → composer opens
- [ ] Composer shows "Connect wallet" message if disconnected

### 2.4 Disconnect Flow

- [ ] Click wallet address → disconnect option visible
- [ ] Disconnect → sidebar shows "Not Connected"
- [ ] Navigate to Wallet tab → shows auth gate again

## 🔄 Phase 3: Web Browser Verification

### 3.1 Chrome/Edge (Chromium)

- [ ] Visit `http://localhost:3000` in Chrome
- [ ] Connect wallet via MetaMask extension
- [ ] All features work (same as Electron checklist)

### 3.2 Firefox

- [ ] RainbowKit works with Firefox
- [ ] MetaMask extension connects
- [ ] No console errors specific to Firefox

### 3.3 Safari (macOS)

- [ ] Wallet connection works
- [ ] UI renders correctly (Tailwind compatibility)

## 🔄 Phase 4: Build & Package

### 4.1 Production Build

- [ ] `cd v13/atlas && npm run build` succeeds
- [ ] No TypeScript errors
- [ ] Bundle size acceptable (<5MB initial)
- [ ] No warnings about missing deps

### 4.2 Electron Package

- [ ] `npm run electron:build` creates distributable
- [ ] Windows: `.exe` installer works
- [ ] macOS: `.dmg` works (if on Mac)
- [ ] Linux: `.AppImage` works (if on Linux)

### 4.3 Packaged App Test

- [ ] Installed app launches correctly
- [ ] Wallet connects in packaged version
- [ ] No dev server references in logs

## 🔄 Phase 5: Backend Health

### 5.1 API Stability

- [ ] `curl http://127.0.0.1:8001/health` returns 200
- [ ] Auth nonce endpoint works
- [ ] Auth verify endpoint works
- [ ] All v18 endpoints respond correctly

### 5.2 Error Handling

- [ ] Backend returns proper 404 for missing routes
- [ ] Auth errors show user-friendly messages
- [ ] Network errors don't crash frontend

## 📊 Final Metrics

- **Navigation Tests:** 3/3 passing
- **Wallet Connection:** 0/1 (needs verification)
- **Console Errors:** 0 (target)
- **Build Success:** TBD
- **Package Success:** TBD

## 🚢 Ship Criteria

All of these must be true:

- [ ] Wallet connects in Electron desktop app
- [ ] Wallet connects in web browsers
- [ ] Production build succeeds
- [ ] Packaged Electron app works
- [ ] No critical console errors
- [ ] README.md updated with v18 changes
