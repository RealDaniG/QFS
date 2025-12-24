# ATLAS v19 Desktop Application

**Platform:** Windows (macOS/Linux coming soon)  
**Architecture:** Electron + Next.js  
**Version:** v19.0.0-alpha

## Features

- ✅ Full v19 architecture (Trust, IPFS, P2P, Intelligence)
- ✅ Wallet integration (MetaMask/RainbowKit)
- ✅ Real-time P2P mesh connection
- ✅ Offline-first with local IPFS node
- ✅ Desktop notifications for P2P events

## Installation

### For End Users

1. Download `ATLAS-v19-Alpha-Setup.exe` from releases
2. Run installer (accept security warning if unsigned)
3. **IMPORTANT:** Start backend services first:

   ```bash
   cd installation/directory
   docker-compose up -d ipfs
   python -m app.lib.p2p.node
   ```

4. Launch "ATLAS v19" from Start Menu

### For Developers

```bash
cd v13/atlas

# Development mode (with hot reload)
npm run electron:dev

# Build distributable
npm run electron:build
```

## Configuration

### Backend Connection

The Electron app expects:

- **Backend API:** `http://127.0.0.1:8001`
- **P2P Node:** `ws://127.0.0.1:9000/ws`
- **IPFS API:** `http://127.0.0.1:5001`

These can be configured in:

```javascript
// desktop/main.js
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8001';
const P2P_URL = process.env.P2P_URL || 'ws://127.0.0.1:9000/ws';
```

## Troubleshooting

### "Cannot connect to P2P mesh"

- Ensure backend P2P node is running on port 9000
- Check firewall isn't blocking WebSocket connections

### "IPFS content not loading"

- Verify IPFS daemon is running: `docker ps | grep ipfs`
- Check IPFS API is accessible: `curl http://127.0.0.1:5001/api/v0/version`

### "Wallet won't connect"

- Ensure MetaMask extension is installed
- Check Content Security Policy allows Web3 providers
- See CSP configuration in `desktop/main.js`

## Build Configuration

**File:** `desktop/electron-builder.yml`

```yaml
appId: com.atlas.v19
productName: ATLAS v19
directories:
  output: dist
  buildResources: build
files:
  - out/**/*
  - main.js
  - preload.js
win:
  target:
    - nsis
    - portable
  icon: build/icon.ico
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
```

## Known Issues

- **Code signing:** Executable is unsigned (security warnings expected)
- **Auto-update:** Not implemented yet
- **Backend bundling:** Backend must run separately (not bundled in .exe)
