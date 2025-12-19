# Repository Structure

**Version**: v14.0-production
**Purpose**: Define canonical repository organization  
**Status**: Production Ready  
**Last Updated**: 2025-12-19 (v14.0 Release)

## Overview

QFS × ATLAS follows a clean, organized structure with clear separation between core code, tooling, documentation, and artifacts. As of v13.7, the repository has been streamlined with 1,500+ files removed (15% reduction) while preserving all functionality.

## Top-Level Directories

### Core

**`v13/`** - Main codebase

- Purpose: All production code for QFS v13
- Structure:
  - `v13/libs/` - Core libraries (CertifiedMath, BigNum128, EconomicsGuard, HSMF)
  - `v13/atlas/` - ATLAS social modules (Spaces, Wall, Chat)
  - `v13/core/` - Core engines (StateTransitionEngine, CoherenceEngine)
  - `v13/policy/` - Policy, governance, and bounties
  - `v13/handlers/` - CIR-302 and other handlers
  - `v13/guards/` - Constitutional guards
  - `v13/scripts/` - Operational scripts
  - `v13/tests/` - All tests (unit, integration, regression, autonomous)
  - `v13/docs/` - Module-specific documentation
  - `v13/tools/` - Development tools and audit utilities

**`.github/`** - CI/CD workflows

- Purpose: GitHub Actions workflows and automation
- Files:
  - `workflows/ci.yml` - Main CI pipeline
  - `workflows/pre-release.yml` - Release gate
  - `workflows/zero-sim-autofix.yml` - Automated fixes

### Documentation

**`docs/`** - High-level documentation

- Purpose: Project-wide documentation and specifications
- Structure:
  - `docs/root_docs/` - Copies of root documentation (BOUNTIES, CI_IMPROVEMENTS, etc.)
  - Architecture docs
  - Design specs
  - API documentation
  - Governance docs

**Root-level docs** (canonical):

- `README.md` - Project overview and quickstart
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `CONTRIBUTORS.md` - Contributor list
- `REGRESSION.md` - Regression hash and replay verification
- `SECURITY_NOTES.md` - Security assumptions and deviations
- `CI_IMPROVEMENTS.md` - CI/CD improvements and roadmap
- `BOUNTIES.md` - Bounty system documentation
- `REPO_STRUCTURE.md` - This file
- `SYSTEM_MAP.md` - Ecosystem map (Product vs Protocol)
- `LICENSE.ATLAS.md` - License information

### v15 (Next-Gen Protocol)

**`v15/`** - Autonomous Governance & PoE

- Purpose: Structural Verifiability & PoE Infrastructure
- Structure:
  - `v15/atlas/governance/` - Enhanced governance engine (PoE-native)
  - `v15/tools/` - Verification tooling (`verify_poe.py`, `replay_gov_cycle.py`)
  - `v15/config/` - v15 Configurations

### Tooling & Infrastructure

**`monitoring/`** - Observability framework

- Purpose: Metrics, dashboards, and monitoring
- Structure:
  - `monitoring/collectors/` - Metrics collectors
  - `monitoring/MONITORING_FRAMEWORK.md` - Framework documentation

**`scripts/`** - Standalone utility scripts

- Purpose: One-off tools and utilities not part of v13/scripts
- Examples: Build scripts, deployment tools, data migration

**`logs/`** - Log files and error reports

- Purpose: Centralized logging
- Structure:
  - `logs/error_reports/` - Organized error logs (ast_errors, econ_errors, type_check_report, etc.)

**`.agent/`** - AI agent workflows

- Purpose: Agent-specific workflows and configurations
- Structure:
  - `.agent/workflows/` - Workflow definitions

### Artifacts & Archives

**`archive/`** - Historical artifacts

- Purpose: Preserve old reports, logs, and deprecated files
- Subdirectories:
  - `archive/test_logs/` - Old test outputs and coverage reports
  - `archive/violation_reports/` - Historical Zero-Sim reports
  - `archive/phase3_artifacts/` - Phase 3 completion artifacts

**`evidence/`** - Compliance evidence

- Purpose: Audit trails and compliance artifacts
- Contents: Logs, reports, and evidence for audits
- Subdirectories:
  - `evidence/poe_artifacts/` - Proof-of-Execution artifacts (v15.3 index)
  - `evidence/governance_index.json` - Hash-chained index

**`reports/`** - Generated reports

- Purpose: CI-generated reports and analysis
- Contents: Test reports, coverage, security scans

### Development

**`deploy/`** - Deployment configurations

- Purpose: Deployment scripts and configurations

**`checkpoints/`** - System state checkpoints

- Purpose: Autonomous validation checkpoints
- Created by: `v13/tests/autonomous/phase_0_scan.py`

## v13 Internal Structure

### Core Libraries (`v13/libs/`)

- `BigNum128.py` - Fixed-point arithmetic
- `CertifiedMath.py` - Deterministic math operations
- `economics/` - Economic guards and constants
  - `EconomicsGuard.py` - Constitutional bounds enforcement
  - `economic_constants.py` - System constants
- `governance/` - Governance modules
  - `NODInvariantChecker.py` - NOD invariant enforcement
- `integration/` - Integration engines
  - `StateTransitionEngine.py` - State transitions
  - `CoherenceEngine.py` - Coherence validation
- `pqc/` - Post-quantum cryptography
- `keystore/` - Key management

### Policy & Governance (`v13/policy/`)

- `bounties/` - Bounty system
  - `bounty_state_machine.py` - Bounty lifecycle
  - `bounty_schema.py` - Bounty data structures
  - `bounty_events.py` - Economic events
- `treasury/` - Treasury management
  - `dev_rewards_treasury.py` - Developer rewards (BigNum128 aligned)

### Handlers (`v13/handlers/`)

- `CIR302_Handler.py` - Constitutional error handling with explainability

### Tests (`v13/tests/`)

- `governance/` - Governance tests
  - `test_bounty_integration.py` - Bounty integration tests
- `autonomous/` - Autonomous validation framework
  - `phase_0_scan.py` - Environment scanner
  - `phase_2_guards.py` - Guard validator
  - `validate_guards.py` - Simplified validator
  - `debug_guards.py` - Diagnostic tool
  - `run_autonomous_validation.py` - Master controller
  - `README.md` - Framework documentation

### Tools (`v13/tools/`)

- `audit/` - Audit utilities (moved from tools_root)

## Root-Level Files

### Essential

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quickstart, links |
| `LICENSE.ATLAS.md` | License and legal |
| `pyproject.toml` | Python project metadata |
| `pytest.ini` | Pytest configuration |
| `setup.cfg` | Python setup configuration |
| `mypy.ini` | MyPy type checking configuration |
| `.gitignore` | Git ignore rules |
| `.python-version` | Python version specification |
| `.pre-commit-config.yaml` | Pre-commit hooks |

### Documentation

| File | Purpose |
|------|---------|
| `CHANGELOG.md` | Version history |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CONTRIBUTORS.md` | Contributor list |
| `REGRESSION.md` | Regression hash documentation |
| `SECURITY_NOTES.md` | Security assumptions and trust model |
| `CI_IMPROVEMENTS.md` | CI/CD improvements and roadmap |
| `BOUNTIES.md` | Bounty system documentation |
| `REPO_STRUCTURE.md` | This file |
| `ROOT_CLEANUP_SUMMARY.md` | Cleanup summary |

### v14 Production

| File | Purpose |
|------|---------|
| `v14_regression_hash.txt` | Canonical regression hash |
| `v14_trace.log` | Regression scenario output |

### Scripts

| File | Purpose |
|------|---------|
| `run_atlas.bat` | Windows ATLAS launcher |
| `atlas_launch.bat` | Alternative launcher |
| `atlas_aio_launcher.bat` | All-in-one launcher |
| `run_tests.ps1` | Test runner |
| `test_log.bat` | Test logging script |
| `cleanup_repository.ps1` | Backup file cleanup script |
| `deep_cleanup.ps1` | Comprehensive cleanup script |

### Active Working Files

| File | Purpose |
|------|---------|
| `task.md` | Current task tracking |

## Cleanup Summary (v13.7)

### Removed (1,500+ files)

- ✅ 1,393 backup files (`.batch2/3/4.backup`)
- ✅ `v13/legacy_root/` (122 items)
- ✅ `v13/libs_root/` (consolidated to `v13/tests/libs_checks/`)
- ✅ `v13/services_root/` (duplicate files)
- ✅ `v13/tools_root/` (consolidated to `v13/tools/audit/`)
- ✅ Outdated root folders: `AGENT/`, `CODERV1/`, `CURRENCY/`, `src/`, `tests/`, `zero_sim/`, `test_logs/`, `structure_analysis/`, `wiki_migration/`, `artifacts/`
- ✅ Root-level test files: `debug_test.py`, `debug_imports.py`, `test_wallet.py`, etc.

### Organized

- ✅ Error logs → `logs/error_reports/`
- ✅ Documentation → `docs/root_docs/`
- ✅ Audit tools → `v13/tools/audit/`
- ✅ Test utilities → `v13/tests/libs_checks/`

### Impact

- **Root folders**: 28 → 18 (-36%)
- **v13 items**: 1,422 → 1,276 (-10%)
- **Total reduction**: ~15% (1,500+ files)
- **Functionality**: 100% preserved
- **Imports**: Zero breaking changes

## Where to Put New Files

### New Documentation

- **High-level/project-wide**: `docs/` or root (if canonical like REGRESSION.md)
- **Module-specific**: `v13/docs/`
- **Evidence/audit**: `evidence/`

### New Scripts

- **Operational/CI**: `v13/scripts/`
- **Standalone tools**: `scripts/`
- **Experimental**: `.agent/`

### New Tests

- **All tests**: `v13/tests/` (unit, integration, regression, autonomous)
- **Governance tests**: `v13/tests/governance/`
- **Autonomous validation**: `v13/tests/autonomous/`

### New Code

- **Production code**: `v13/` (appropriate subdirectory)
- **Libraries**: `v13/libs/`
- **Policy**: `v13/policy/`
- **Handlers**: `v13/handlers/`

### Artifacts

- **CI reports**: `reports/` (auto-generated, gitignored)
- **Evidence**: `evidence/`
- **Historical**: `archive/`
- **Checkpoints**: `checkpoints/`

## Maintenance

### Regular Cleanup (Monthly)

1. Review root for new loose files
2. Move generated reports to archive/
3. Update .gitignore for new temp file patterns
4. Consolidate duplicate documentation
5. Run `cleanup_repository.ps1` if backup files accumulate

### Before Major Releases

1. Verify all canonical docs are up-to-date
2. Archive old phase artifacts
3. Clean up reports/ directory
4. Update this REPO_STRUCTURE.md
5. Run full test suite: `pytest v13/tests/`
6. Verify autonomous validation: `python v13/tests/autonomous/validate_guards.py`

## Constitutional Guarantees

The repository structure supports the following constitutional guarantees:

- **0.5% RES Resonance Cap**: Enforced via `v13/libs/economics/EconomicsGuard.py`
- **25% NOD Voting Power**: Enforced via `v13/libs/governance/NODInvariantChecker.py`
- **Deterministic Replay**: Ensured by `v13/libs/integration/StateTransitionEngine.py`
- **BigNum128 Alignment**: All economic paths use `v13/libs/BigNum128.py`
- **Zero-Simulation Compliance**: Validated by autonomous framework

---

**Last Updated**: 2025-12-19 (v14.0-production)  
**Next Review**: Before v15.0 design phase  
**Cleanup Status**: ✅ Complete (1,500+ files removed)
