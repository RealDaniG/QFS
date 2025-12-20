# Repository Structure

**Version**: v14.0-social-layer  
**Purpose**: Define canonical repository organization  
**Status**: Production Ready

## Overview

QFS × ATLAS follows a clean, organized structure with clear separation between core code, tooling, documentation, and artifacts.

## Top-Level Directories

### Core

**`v13/`** - Main codebase

- Purpose: All production code for QFS v13
- Structure:
  - `v13/libs/` - Core libraries (CertifiedMath, BigNum128, HSMF)
  - `v13/atlas/` - ATLAS social modules (Spaces, Wall, Chat)
  - `v13/core/` - Core engines (StateTransitionEngine, CoherenceEngine)
  - `v13/policy/` - Policy and governance
  - `v13/scripts/` - Operational scripts (zero_sim_analyzer, etc.)
  - `v13/tests/` - All tests (unit, integration, regression)
  - `v13/docs/` - Module-specific documentation

**`.github/`** - CI/CD workflows

- Purpose: GitHub Actions workflows and automation
- Files:
  - `workflows/ci.yml` - Main CI pipeline
  - `workflows/pre-release.yml` - Release gate
  - `workflows/zero-sim-autofix.yml` - Automated fixes

### Documentation

**`docs/`** - High-level documentation

- Purpose: Project-wide documentation and specifications
- Recommended contents:
  - Architecture docs
  - Design specs
  - API documentation
  - Governance docs

**Root-level docs** (canonical):

- `README.md` - Project overview and quickstart
- `REGRESSION.md` - Regression hash and replay verification
- `SECURITY_NOTES.md` - Security assumptions and deviations
- `CI_IMPROVEMENTS.md` - CI/CD improvements and roadmap
- `LICENSE.ATLAS.md` - License information

### Tooling & Infrastructure

**`monitoring/`** - Observability framework

- Purpose: Metrics, dashboards, and monitoring
- Structure:
  - `monitoring/collectors/` - Metrics collectors
  - `monitoring/MONITORING_FRAMEWORK.md` - Framework documentation

**`scripts/`** - Standalone utility scripts

- Purpose: One-off tools and utilities not part of v13/scripts
- Examples: Build scripts, deployment tools, data migration

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

**`reports/`** - Generated reports

- Purpose: CI-generated reports and analysis
- Contents: Test reports, coverage, security scans

### Development

**`tests/`** - Legacy test directory (deprecated)

- Purpose: Old test location, now consolidated under v13/tests
- Status: Being phased out

**`src/`** - Legacy source directory (deprecated)

- Purpose: Old source location, now consolidated under v13/
- Status: Being phased out

**`sandbox/`** (optional, create as needed)

- Purpose: Experimental code and prototypes
- Not tracked in production branches

## Root-Level Files

### Essential

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quickstart, links |
| `LICENSE.ATLAS.md` | License and legal |
| `pyproject.toml` | Python project metadata |
| `pytest.ini` | Pytest configuration |
| `setup.cfg` | Python setup configuration |
| `.gitignore` | Git ignore rules |
| `.python-version` | Python version specification |

### v14 Production

| File | Purpose |
|------|---------|
| `REGRESSION.md` | Regression hash documentation |
| `SECURITY_NOTES.md` | Security assumptions and trust model |
| `CI_IMPROVEMENTS.md` | CI/CD improvements and roadmap |
| `v14_regression_hash.txt` | Canonical regression hash |
| `v14_trace.log` | Regression scenario output |

### Documentation

| File | Purpose |
|------|---------|
| `CHANGELOG_P0.md` | Phase 0 changelog |
| `CHANGELOG_P3.md` | Phase 3 changelog |
| `CHANGELOG_SESSIONS.md` | Session-based changelog |
| `P0_COMPLETION_CERTIFICATE.md` | Phase 0 completion |
| `P0_TEST_SUMMARY.md` | Phase 0 test summary |
| `QFS_V13_VALUE_NODE_EXPLAINABILITY.md` | Value node documentation |
| `ZERO_SIM_VALUE_NODE_STATUS.md` | Zero-Sim status |
| `zero_sim_architectural_exceptions.md` | Architectural exceptions |
| `zero_sim_manual_review.md` | Manual review notes |

### Temporary/Generated (should be in .gitignore)

| File | Purpose | Action |
|------|---------|--------|
| `violation_report.json` | CI-generated | Move to reports/ or gitignore |
| `final_violation_report.json` | CI-generated | Move to archive/ |
| `phase3_progress.json` | Progress tracking | Move to archive/ |
| `task.md` | Working notes | Keep at root (active) |
| `zero_sim_phase3_ready.flag` | Flag file | Move to archive/ |

### Scripts

| File | Purpose | Action |
|------|---------|--------|
| `run_atlas.bat` | Windows launcher | Keep at root |
| `run_tests.ps1` | Test runner | Keep at root |

## Where to Put New Files

### New Documentation

- **High-level/project-wide**: `docs/` or root (if canonical like REGRESSION.md)
- **Module-specific**: `v13/docs/`
- **Evidence/audit**: `evidence/`

### New Scripts

- **Operational/CI**: `v13/scripts/`
- **Standalone tools**: `scripts/`
- **Experimental**: `sandbox/` or `.agent/`

### New Tests

- **All tests**: `v13/tests/` (unit, integration, regression)
- **Legacy location**: `tests/` is deprecated, don't add here

### New Code

- **Production code**: `v13/` (appropriate subdirectory)
- **Experimental**: `sandbox/` (not tracked in main)

### Artifacts

- **CI reports**: `reports/` (auto-generated, gitignored)
- **Evidence**: `evidence/`
- **Historical**: `archive/`

## Cleanup Guidelines

### Files to Keep at Root

- Essential config (pyproject.toml, pytest.ini, setup.cfg)
- Canonical docs (README, REGRESSION, SECURITY_NOTES, CI_IMPROVEMENTS)
- v14 artifacts (v14_regression_hash.txt, v14_trace.log)
- Active working files (task.md)
- Launchers (run_atlas.bat, run_tests.ps1)

### Files to Move

- Old reports → `archive/`
- Generated JSON → `reports/` or `.gitignore`
- Experimental scripts → `sandbox/` or `scripts/`
- Legacy docs → `archive/` or consolidate

### Files to Delete

- Duplicate files
- Obsolete temp files
- Old build artifacts (if not needed for audit)

## Maintenance

### Regular Cleanup (Monthly)

1. Review root for new loose files
2. Move generated reports to archive/
3. Update .gitignore for new temp file patterns
4. Consolidate duplicate documentation

### Before Major Releases

1. Verify all canonical docs are up-to-date
2. Archive old phase artifacts
3. Clean up reports/ directory
4. Update this REPO_STRUCTURE.md

---

**Last Updated**: 2025-12-18 (v14.0 release)  
**Next Review**: Before current baseline.0 release
