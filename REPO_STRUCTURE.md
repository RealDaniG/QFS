# Repository Structure

**Version**: v17.0.0-beta-governance-bounties
**Purpose**: Define canonical repository organization for v17 (v13 legacy + v15 PoE + v17 governance/bounties/social/advisory)
**Status**: Beta (F-Layer Complete)
**Last Updated**: 2025-12-20 (v17.0 Beta)
**Next Review**: Start of v18 Design (Multi-Node Distribution)

## Overview

QFS × ATLAS operates as a multi-layered engine. The repository reflects the generational evolution of the protocol:

- **v13**: Legacy engine and economic baseline (constitutional invariants, SafeMath).
- **v15**: Proof-of-Execution (PoE), EvidenceBus, and verification infrastructure.
- **v16**: Authentication, Session Management, and User Tables.
- **v17**: Deterministic Governance, Bounties, Social Surface, and Agent Advisory (Layer D).

## Top-Level Directories

### Core

**`v17/`** - Current F-Layer (Governance, Bounties, Social)

- Purpose: Canonical deterministic logic for the current beta
- Structure:
  - `v17/governance/` - Proposals, Voting, Execution (Deterministic F-Layer)
  - `v17/bounties/` - Bounty lifecycle and reward allocation
  - `v17/social/` - Social surface (Threads, Disputes)
  - `v17/agents/` - Layer D Advisory (Heuristics, Listeners)
  - `v17/ui/` - Projections and DTO builders
  - `v17/tests/` - v17-specific unit and integration tests

**`v15/`** - PoE & Evidence Infrastructure

- Purpose: Structural Verifiability & EvidenceBus
- Structure:
  - `v15/evidence/` - EvidenceBus implementation
  - `v15/utils/` - Deterministic utilities (Timestamping)
  - `v15/auth/` - EIP-191 Wallet Authentication (v16 basis)
  - `v15/ui/` - Admin Dashboard foundations

**`v13/`** - Legacy Engine & Economic Baseline

- Purpose: Constitutional invariants and regression baseline
- Structure:
  - `v13/libs/` - Core libraries (CertifiedMath, BigNum128, EconomicsGuard)
  - `v13/tests/` - Legacy test suite (Regression barriers)

**`.github/`** - CI/CD workflows

- Purpose: GitHub Actions workflows and automation
- Files:
  - `workflows/ci.yml` - Main CI pipeline (v17 tests + Zero-Sim)
  - `workflows/autonomous_verification.yml` - Zero-Sim enforcement

### Documentation

**`docs/`** - High-level documentation

- Purpose: Project-wide documentation and specifications
- Structure:
  - `docs/RELEASES/` - Release notes and implementation summaries (v16, v17)
  - `docs/architecture/` - System design docs

**Root-level docs** (canonical):

- `README.md` - Project overview and quickstart
- `REPO_STRUCTURE.md` - This file
- `SYSTEM_MAP.md` - Ecosystem map (Product vs Protocol)
- `LAYER_D_ADVISORY_COMPLETE.md` - Advisory system specs
- `V17_IMPLEMENTATION_COMPLETE.md` - v17 F-Layer sign-off

### Artifacts & Archives

**`evidence/`** - Compliance evidence

- Purpose: Audit trails and compliance artifacts
- Contents: `governance_index.json` (PoE Chain)

**`scripts/`** - Common Utilities

- `scripts/check_zero_sim.py` - Zero-Simulation Enforcer
- `scripts/smoke_test_layer_d.py` - Advisory Smoke Test

## Where to Put New Files

### New Code

- **Governance/Bounties/Social**: `v17/` (appropriate submodule)
- **Advisory Agents**: `v17/agents/`
- **Core Infrastructure (Bus, Auth)**: `v15/`

### New Tests

- **Feature Tests**: `v17/tests/`
- **Regression/Invariant Checks**: `v13/tests/` (only if strictly legacy-bound)

### New Documentation

- **Feature Specs**: `docs/` or Root (if major)
- **Release Notes**: `docs/RELEASES/`

## Maintenance (v17 Pipeline)

### Before Major Releases

1. Run Pipeline: `python run_pipeline.py`
2. Test Suite: `pytest v17/tests` and `pytest v13/tests`
3. Zero-Sim Check: `python scripts/check_zero_sim.py --fail-on-critical`
4. Update `REPO_STRUCTURE.md` if layout changes

## Constitutional Guarantees

The repository structure supports the following constitutional guarantees:

- **0.5% RES Resonance Cap**: Enforced via `v13/libs/economics/EconomicsGuard.py`
- **Deterministic Replay**: Ensured by `v15/evidence/bus.py` (EvidenceBus) and v17 F-Layers
- **Zero-Simulation Compliance**: Validated by `scripts/check_zero_sim.py`
- **Advisory-Only Agents**: Enforced by `v17/agents/` architecture (read-only + emit advisory events)

---

**Last Updated**: 2025-12-20 (v17.0-beta)
**Next Review**: v18 (Distributed Consensus)
