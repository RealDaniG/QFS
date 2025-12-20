# Testing Guide

This document outlines the testing strategy and commands for the QFS × ATLAS V18 system.

## 🧪 Testing Strategy & Authority

Because of environmental constraints with agent-driven browsers (CDP), we rely on the following authoritative sources for verification:

| Verification Layer | Authority | Tool |
| :--- | :--- | :--- |
| **API / Backend** | `verify_atlas_e2e.py` | Python Script (Requests) |
| **Auth Protocol** | `verify_auth.py` | Python Script (Eth-Account) |
| **UI Rendering** | `npm run test:e2e` | Playwright (Chromium Headless) |
| **Regression** | `pytest` | Backend Unit Tests |

**Note**: The "Browser Subagent" tool is not supported in this environment due to CDP instability. **Playwright** is the canonical UI verification tool.

---

## ⚡ Full System Verification (Canonical)

To verify the entire V18 integration (Backend, Frontend, Auth, E2E Flows) in one go, use the **Orchestrator**:

```powershell
powershell -ExecutionPolicy Bypass -File run_atlas_full.ps1
```

This script:

1. Starts the Backend (Port 8001) and Frontend (Port 3000).
2. Waits for health checks to pass.
3. Runs:
   - `verify_atlas_e2e.py` (API Check)
   - `verify_auth.py` (Auth Flow)
   - `pytest` (Route Regression)
   - `npm run test:e2e` (Playwright UI Smoke Tests)
4. Logs results to `logs/atlas_full_run.log`.

**Exit Code 0** indicates a fully healthy system where all critical checks passed.

---

## 🧪 Detailed Testing Layers

### 1. Unit & Regression Tests (Backend)

**Scope**: Core logic, API Route verification via `app.routes`.
**Location**: `v13/atlas/src/tests/` and `v13/tests/`

**How to Run**:

```bash
# Set PYTHONPATH to repo root
# Windows (PowerShell)
$env:PYTHONPATH = "path\to\repo\V13"
python -m pytest v13/atlas/src/tests/test_routes_v18.py
```

### 2. API End-to-End Tests

**Scope**: Connectivity, HTTP Status Codes, Data Structure verification (Live Backend).
**Verification Scripts**:

| Script | Purpose |
| :--- | :--- |
| `scripts/verify_auth.py` | verifies the complete Wallet Auth flow (Nonce -> Sign -> Login). **Canonical Auth Test.** |
| `v13/scripts/verify_atlas_e2e.py` | Verifies existence and JSON response of all major V18 endpoints. |

**How to Run**:

```bash
# Ensure Backend is running (port 8001)
python scripts/verify_auth.py
python v13/scripts/verify_atlas_e2e.py
```

### 3. UI End-to-End Tests (Playwright)

**Scope**: Frontend user flows, Component rendering, API wiring verification in browser.
**Location**: `v13/atlas/tests/e2e/`

**How to Run**:

```bash
cd v13/atlas
npm run test:e2e
```

*Tests cover: Homepage Layout, Governance Loading, Feed Data Interception, Wallet View.*
*Note: We rely on Playwright to verify UI state as agent browsers may be unstable.*

### 4. Compliance & Invariants

**Scope**: Determinism enforcement, Zero-Simulation checks.

**How to Run**:

```bash
python scripts/check_zero_sim.py --fail-on-critical
```

---

## 🐞 Troubleshooting

- **Environment**: If `pytest` fails with ImportErrors, verify `PYTHONPATH`.
- **Mocking**: Dev environment assumes `QFS_FORCE_MOCK_PQC=1`.
- **Ports**: Backend must be on `8001` for E2E scripts and Playwright Config `3000`/`8001`.
