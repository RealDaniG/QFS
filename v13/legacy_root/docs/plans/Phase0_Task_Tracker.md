# Phase 0: Preparation Task Tracker

## Environment Lockdown
- [x] Install Node.js 18+ and Python 3.10+ (Node.js v22.20.0, Python 3.13.7)
- [x] Lock all dependencies (package-lock.json / requirements.txt)
- [x] Verify deterministic compiler versions (Solidity, TS/JS, Python)
- [ ] Confirm PostgreSQL 14+ setup and migrations
- [x] Create empty audit log folder: /audit_logs

## Baseline Repository Snapshot
- [x] Record current git commit hash (b8eddf34ef4bfc63575b06e8f1b9f694e3d53e8d)
- [x] Create V12 full backup (QFS/V12_backup)
- [x] Document current folder/file structure in docs/V12_FileMap.md
- [x] Create new GitHub repository with only V13 folder

## Audit & Enforcement Tooling
- [x] Install/verify AST-based Zero-Simulation Checker (scripts/zero-sim-ast.js)
- [x] Prepare CertifiedMath test harness (tests/certifiedmath/)
- [x] Initialize PQC test environment (Dilithium/Kyber precompiled)
- [x] Implement refactored CertifiedMath.py with full 128-bit unsigned integer support
- [x] Apply CertifiedMath.py refinements (type hints, edge case handling, export_log helper)
- [x] Create CertifiedMath API service for Open-A.G.I integration
- [x] Implement CertifiedMath API endpoints with PQC attestation
- [x] Add audit logging and deterministic operation tracking