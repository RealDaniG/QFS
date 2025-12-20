# Repository Structure

**Version**: Structure-v18.0 (Integration Phase)
**Purpose**: Define canonical repository organization and where new work should go.
**Status**: Source of Truth for Repository Layout.

## Overview

QFS × ATLAS is a hybrid system combining a legacy deterministic engine (`v13`), a next-gen authentication layer (`v15`), and a distributed backbone (`v18`).

### 📂 Top-Level Directory Map

| Directory | Purpose | Key Substructures |
| :--- | :--- | :--- |
| **`v13/`** | **Application & Core Engine**. Contains the ATLAS frontend/backend and the QFS economic logic. | `atlas/`, `core/`, `tests/` |
| **`v18/`** | **Distributed Backbone**. Consensus, clustering, and PQC anchoring simulation. | `consensus/`, `pqc/`, `cluster/` |
| **`v15/`** | **Identity & Auth**. Authentication primitives and EvidenceBus foundations. | `auth/`, `evidence/` |
| **`docs/`** | **Documentation**. Specs, guides, status reports. | `RELEASES/`, `architecture/` |
| **`scripts/`** | **Tooling**. Root-level maintenance and verification scripts. | `verify_auth.py`, `check_zero_sim.py` |
| **`tests/`** | **Global Tests**. (Emerging consolidation point). | |
| **`evidence/`**| **Artifacts**. Audit trails and PoE chains. | |

---

## 🏗️ Detailed Structure

### `v13/` - Application & Core Engine

This is the working directory for the active ATLAS application.

- **`v13/atlas/`**: The **Integrated V18 Application**.
  - `src/app/` (Next.js Frontend) - Includes `GovernanceInterface` and `DistributedFeed`.
  - `src/api/` (FastAPI Backend) - Routes for `v18/governance`, `v18/content`, `v1/wallets`.
  - `src/lib/` - Shared business logic and singletons (`RealLedger`, `GovernanceService`).
- **`v13/libs/`**: Core economic libraries (`CertifiedMath`, `EconomicsGuard`).

### `v18/` - Distributed Backbone

Contains the distributed systems logic separate from the web application.

- `v18/consensus/`: Raft implementation.
- `v18/pqc/`: Post-Quantum Cryptography batching services.
- `v18/cluster/`: Node simulation and topology definitions.

### `v15/` - Identity & Auth

- `v15/auth/`: Wallet authentication logic (EIP-191).
- `v15/evidence/`: EvidenceBus structures.

---

## 🔗 V18 Integration & Readiness

The repository is currently in the **V18 Integration Phase**. Key Integration documents are located in `docs/`:

- **[Integration Status](docs/V18_INTEGRATION_STATUS_DETAILED.md)**: Current state of Backend/Frontend wiring.
- **[Deployment Checklist](docs/V18_DEPLOYMENT_CHECKLIST.md)**: Infra diagram and go-live steps.
- **[Security Debt](docs/SECURITY_DEBT.md)**: Known gaps (CORS, Token Storage).
- **[Observability Spec](docs/OBSERVABILITY_SPEC.md)**: Logging standards (`logs/`).
- **[UX Polish Backlog](docs/UX_POLISH_BACKLOG.md)**: Frontend improvements needed.

---

## 📍 Where to Put New Files

| Content Type | Target Directory | Notes |
| :--- | :--- | :--- |
| **Frontend UI/Components** | `v13/atlas/src/components/` | Application layer code. |
| **Backend API Routes** | `v13/atlas/src/api/routes/` | Expose via `main_minimal.py`. |
| **Consensus/Backbone Logic** | `v18/[submodule]/` | Distributed system core. |
| **Verification Scripts** | `scripts/` | If general purpose. |
| **Tests (Backbone)** | `v18/tests/` | |
| **Tests (Application)** | `v13/atlas/src/tests/` | Or `tests/e2e/` (Playwright). |
| **Documentation** | `docs/` or Root | Link in `DOCS_INDEX.md`. |

---

## 🧹 Maintenance & Cleanup

**Before Major Releases:**

1. **Run Pipeline**: `python run_pipeline.py`
2. **Verify Zero-Sim**: `python scripts/check_zero_sim.py`
3. **Run Full Test Suite**: See [TESTING.md](TESTING.md).
4. **Update Structure Docs**: Ensure this file matches reality.

---

**Last Updated**: 2025-12-20 (Post-V18 Integration)
