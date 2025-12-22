# ATLAS v14 v2 - Orchestration & Verification Runbook

This document summarizes the changes made to stabilize the ATLAS v14 v2 baseline and provides instructions for deterministic launch and verification.

## 1. Summary of Changes

### Orchestration Layer

- **[NEW] scripts\check_prerequisites.ps1**: Enforces environment hygiene (Node, Python) and guards against port conflicts (8001, 3000) by checking for `Listen` states.
- **[NEW] scripts\run_atlas_full.ps1**:
  - Aggressively kills existing `node`, `python`, and `electron` processes.
  - Starts Backend on `127.0.0.1:8001`.
  - Starts Proxy on `127.0.0.1:3000`.
  - Launches Electron with `SKIP_BACKEND=true` to prevent redundant processes.
  - Redirects all standard output/error to `logs/` for diagnostics.
- **[MODIFY] launcher.bat**: Updated to sequentially call the PowerShell prerequisites check and then the full orchestration script.

### Configuration Layer

- **[MODIFY] desktop\main.js**: Standardized development URL to `http://127.0.0.1:3000` to avoid flaky `localhost` resolution.
- **[MODIFY] playwright.config.ts**: Standardized `baseURL` to `http://127.0.0.1:3000`.

## 2. Runbook

### How to start ATLAS v14 v2 Desktop (One Command)

Run this from the project root:

```batch
launcher.bat
```

*Wait for the green "ATLAS v14 v2 is now running" message. The Electron window will open automatically.*

### How to run the full E2E suite safely

1. Ensure the system is running (via `launcher.bat`).
2. Open a **separate** terminal.
3. Execute the Playwright suite:

```powershell
npx playwright test tests/e2e/smoke.spec.ts tests/e2e/v18-dashboard-verification.spec.ts --project=chromium --workers=1
```

### Process Cleanup (If needed manually)

If you encounter persistent port conflicts, run this aggressive cleanup:

```powershell
powershell -Command "Stop-Process -Name node, python, electron, 'ATLAS v18 Beta' -Force -ErrorAction SilentlyContinue"
```

## 3. Diagnostics

All system logs are captured in the `logs/` directory:

- `logs/launcher.log`: High-level orchestration steps.
- `logs/backend_stderr.log`: Raw backend errors/info.
- `logs/proxy_stderr.log`: Frontend proxy server activity.
- `logs/electron_stderr.log`: Console output from the Electron window.
