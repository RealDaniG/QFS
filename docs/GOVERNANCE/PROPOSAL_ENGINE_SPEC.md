# Proposal Engine Specification (v15)

## Overview

The Proposal Engine is the deterministic kernel of QFS Autonomous Governance. It manages the lifecycle of proposals, from submission to final execution, ensuring that all state transitions are audit-proof and rule-bound.

## Core Design Principles

### 1. Integer-Only Math (`GOV-I1`)

To prevent non-deterministic behavior across different architectures (e.g., float precision differences), all thresholds and ratios are calculated using **pure integer arithmetic**.

- **Quorum**: `30` (30% of Total NOD Stake)
- **Supermajority**: `66` (66% of Yes/No Votes)

### 2. Canonical Serialization (`GOV-I2`)

Proposal IDs and Proof hashes are generated using a strict, proprietary canonicalization method:

- **JSON**: `sort_keys=True`, `separators=(",", ":")`
- **Encoding**: UTF-8
- **Hash**: SHA3-512

### 3. Proof-of-Execution (`GOV-I3`)

Every finalized proposal generates a **PoE Artifact** that mathematically proves the outcome. This artifact includes:

- Proposal Payload Hash
- Final Vote Tally Snapshot
- Exact Percentages Calculated
- Final Status (PASSED/REJECTED)

## State Machine Phases

1. **DRAFT**: Proposal created but not yet active.
2. **ACTIVE**: Voting is open.
3. **PASSED**: Thresholds met (Quorum & Supermajority).
4. **REJECTED**: Thresholds not met.
5. **EXECUTED**: Payload applied to the Registry.

## Governance Invariants

- **Zero-Sim Compliance**: No non-deterministic logic (randomness, system time) permitted in tallying.
- **Constitutional Protection**: Attempts to modify immutable parameters (e.g., `CHR_DAILY_EMISSION_CAP` is immutable in v15) are strictly rejected by the execution logic.
