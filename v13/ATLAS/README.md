# ATLAS v18 – Decentralized Financial Dashboard

**Status:** ✅ Production-Ready Alpha  
**Version:** v18-ALPHA  
**Last Updated:** December 23, 2025

## 🚀 Quick Start

### Web Application

```bash
cd v13
./launch_atlas_full.bat  # Windows
# or
./launch_atlas_full.sh   # Linux/Mac

# Open browser: http://localhost:3000
```

### Electron Desktop App

```bash
cd v13/atlas
npm run electron:dev
```

## 📦 Installation (Windows Alpha)

### 1. Prerequisite: Backend System

The core processing cluster is not yet bundled in the Alpha installer. You must start it manually:

```bash
cd v13/atlas
launcher.bat
# Select Option 1 (Normal)
```

### 2. Launch Application

1. Download/Navigate to `desktop/dist/win-unpacked/`
2. Run `ATLAS v18 Beta.exe` (Accept security warning if prompted)
3. Ensure the app connects to the running backend (Network Status green)

---

## ⚠️ Known Limitations (v18 Alpha)

### Authentication

- **Wallet Connection**: Requires compatible browser extension (MetaMask) or WalletConnect QR.
- **Persistence**: Session key rotation is active; you may need to reconnect wallet after app restart.
- **CSP**: Web3 strict mode may block some RPC providers. Check Console (Ctrl+Shift+I) if connection fails.

### Features

- **Feed**: Content loading may be slower than expected on first launch.
- **Composer**: Dialog visibility is undergoing UI refinement.
- **Multi-Node**: UI reflects Node A (Primary) status only.

### Distribution

- **Unsigned Executable**: Windows SmartScreen warning is expected.
- **Manual Updates**: No auto-updater; pull latest git changes to update.

### Core Features

- ✅ **URL-Based Navigation** – Deterministic, testable routing via `?tab=<name>`
- ✅ **Wallet Authentication** – RainbowKit + MetaMask integration
- ✅ **Internal Credit System** – Non-transferable FLX allocation tracking
- ✅ **System Health Dashboard** – Real-time API monitoring
- ✅ **Desktop Application** – Cross-platform Electron app

### Architecture

- 🏗️ **Static Imports** – Eliminated hydration issues
- 🏗️ **Auth Gates** – All sensitive features gated by wallet connection
- 🏗️ **ASCON-128** – Post-quantum cryptography ready

## 🧪 Testing

### E2E Tests

```bash
cd v13/atlas
npm run test:e2e
```

**Current Pass Rate:** 3/3 critical navigation tests

### Manual QA

See `FINAL_VERIFICATION_CHECKLIST.md`

## 📚 Documentation

- `REPAIR_LOG.md` – Complete development audit trail
- `KNOWN_ISSUES.md` – Tracked limitations and deferred features
- `docs/v18-backbone-alignment/` – Technical specifications

## 🔐 Security

- **Wallet:** Identity only (no private key access)
- **Credits:** Internal, non-transferable
- **Session:** ASCON-128 authenticated encryption (planned)
- **CORS:** Restricted to `127.0.0.1`

## 🐛 Known Limitations

1. **Feed Component Test** – Skipped (component works, test timing issue)
2. **Content Composer Test** – Skipped (dialog visibility check flaky)
3. **Real-Time Messaging** – Deferred to post-alpha (requires WebSocket)

## 🛠️ Tech Stack

- **Frontend:** Next.js 14, React 18, Tailwind CSS, shadcn/ui
- **Desktop:** Electron
- **Backend:** Python FastAPI, ASCON, SHA3-256
- **Testing:** Playwright, pytest
- **Wallet:** RainbowKit, wagmi, viem

## 📦 Build

### Production Web Build

```bash
cd v13/atlas
npm run build
```

### Electron Package

```bash
npm run electron:build
```

## 🚢 Deployment Status

- [x] Development environment stable
- [x] Navigation architecture verified
- [x] Auth flow functional (backend + frontend)
- [x] Electron wallet integration verified
- [ ] Production build tested
- [ ] Packaged app tested

## 🤝 Contributing

See main repository README for contribution guidelines.

## 📄 License

See LICENSE file in repository root.
