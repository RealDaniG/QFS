# Testing Guide

This document outlines the testing strategy and commands for the QFS × ATLAS V18 system.

## 🧪 Testing Layers

We employ a 4-layer testing strategy to ensure correctness, security, and usability.

### 1. Unit & Regression Tests (Backend)

**Scope**: Core logic, API Route verification.
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
| `scripts/verify_auth.py` | verifies the complete Wallet Auth flow (Nonce -> Sign -> Login). |
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
