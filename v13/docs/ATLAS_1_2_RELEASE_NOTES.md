# ATLAS 1.2 Release Notes

**Version:** 1.2.0 (Zero-Sim)
**Date:** 2025-12-14
**Codename:** "Crystal & Canvas"

## Overview

ATLAS 1.2 represents a major architectural milestone, achieving 100% Zero-Simulation verification across the stack. This release introduces the Explain-This framework, new Artistic (AES) signals, and deeper AEGIS integration for operational governance.

## Key Features

### 1. Explain-This Framework (Zero-Sim)

Users can now inspect the "why" behind every metric:

- **Reward Explainability:** Breakdown of base ATR, bonuses, caps, and guards.
- **Ranking Explainability:** Deterministic sort order justification.
- **Storage Explainability:** Proof of replica placement and integrity.
- **Governance Audit:** Immutable log of all system configuration changes.

### 2. Artistic Evaluation Signal (AES)

New 5-dimensional signal slice:

- **Dimensions:** Composition, Originality, Emotional Resonance, Technical Execution, Cultural Context.
- **AEGIS Boosts:** Reputation-weighted bonuses for "Veteran" and "Established" creators.
- **Zero-Mock:** Pure deterministic evaluation logic.

### 3. Operational Hardening

- **Zero-Mock Compliance:** 0 violations in production code (Strict Enforcement).
- **Contract V1.3:** Mandatory PQC signatures and fail-closed dependency checks.
- **Performance:** Explain-This latency < 50ms verified.

## Breaking Changes

- `HumorSignalAddon` output schema updated to include `reputation_tier` context.
- `StorageEngine` methods now require AEGIS verification or throw `ImportError`.
- Legacy "mock" classes removed from `CoherenceLedger`.

## Compliance Status

- **Zero-Mock:** PASS
- **Types:** PASS
- **Tests:** PASS
- **Audit Integrity:** VERIFIED

## Next Steps

- Governance Voting Portal (ATLAS 1.3)
- Knowledge Graph Signal Slice
