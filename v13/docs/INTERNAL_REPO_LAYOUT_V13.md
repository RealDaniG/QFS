# V13 Repository Layout

This document describes the target directory structure for the Atlas x QFS V13 repository. The goal is a clean root directory with all code, tests, and documentation consolidated under `v13/`.

## Root Directory

The following files are allowed at the repository root:

- `README.md`
- `LICENSE`
- `pyproject.toml`
- `pytest.ini` (or config in pyproject.toml)
- `.gitignore`
- CI/CD configuration files (e.g., `.github/`)

## `v13/` Structure

All application code, tests, and documentation reside here.

### `v13/atlas_api/`

Contains the gateway, router, API models, and high-level interface logic.

- *Source:* `src/atlas_api/`

### `v13/core/`

Core protocol logic, including CoherenceEngine, CoherenceLedger, TokenStateBundle, and DeterministicTime.

- *Source:* `src/core/`

### `v13/guards/`

Security and invariant guards (AEGISGuard, SafetyGuard, etc.).

- *Source:* `src/guards/`

### `v13/libs/`

Shared libraries including CertifiedMath, cryptographic libs (PQC), economics libs, and governance utilities.

- *Source:* `src/libs/`

### `v13/services/`

Microservices or service integrations (Notification, Storage, etc.).

- *Source:* `src/services/`

### `v13/policy/`

Policy engine and configuration files.

- *Source:* `src/policy/`

### `v13/tests/`

All test files, including unit, integration, and property-based tests.

- *Source:* `tests/` and loose `test_*.py` files.

### `v13/docs/`

All documentation, audits, and evidence.

- **`protocol/`**: Specifications and protocol design docs.
- **`governance/`**: Governance summaries and dashboards (`GOVERNANCE_*.md`, `OBSERVATION_*.md`).
- **`audit/`**: Audit reports and resolution summaries (`CORRECTED_AEGIS_AUDIT_REPORT.md`, `AUDIT_SUMMARY.md`).
- **`summaries/`**: Implementation summaries (`FINAL_AEGIS_IMPLEMENTATION_SUMMARY.md`, `STRESS_TESTING_ENHANCEMENTS.md`).
- **`roadmaps/`**: Progress tracking and planning (`P2_PROGRESS.md`, `TODO_*.md`, `ROADMAP-*.md`).
- **`client/`**: Client integration guides (`CLIENT_INTEGRATION_GUIDE.md`).
- **`evidence/`**: JSON evidence files (`*_report.json`, `*_audit_report.json`).

## Import Strategy

- Internal imports should be relative where possible (e.g., `from ..core import CoherenceEngine`).
- Absolute imports should use the `v13` prefix (e.g., `from v13.core.CoherenceEngine import CoherenceEngine`).
