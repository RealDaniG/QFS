# API Contract: Open-A.G.I Read-Only Layer

**Version**: v13-contracts-2025-12-18
**Status**: ACTIVE
**Policy**: Breaking changes require schema version bump + test update in `test_api_contracts.py`.

## 1. Overview

This interface defines the read-only contract for external AI agents (including the Open-A.G.I swarm) to consume signals from the QFS ecosystem without direct write access to the ledger.

## 2. Invariants

- **Read-Only**: Agents cannot mutate state through this interface.
- **Verification**: All signals must be PQC-signed by a recognized QFS issuer.
- **Rate-Limited**: Access is subject to global throughput caps.

## 3. Data Models

Reference `v13.libs.canonical.models`.

### 3.1 AdvisorySignal

The primary unit of consumption for AI agents.

- `signal_id`: Unique trace ID.
- `issuer_id`: QFS Node ID.
- `payload`: Structured advice or inference result.
- `signature`: Verifiable proof of origin.

## 4. Access Patterns

### `GET /api/v1/signals/feed`

- **Query Params**: `topic`, `min_confidence`
- **Output**: Stream of `AdvisorySignal`

### `GET /api/v1/ledger/snapshot`

- **Output**: Merkle root and recent block headers (for verification).
