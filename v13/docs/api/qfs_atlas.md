# API Contract: QFS <-> ATLAS

**Version**: v13-contracts-2025-12-18
**Status**: ACTIVE
**Polcy**: Breaking changes require schema version bump + test update in `test_api_contracts.py`.

## 1. Overview

This interface defines the strictly typed boundary between the Quantum Financial System (QFS) backend and the ATLAS user interface. All data exchange MUST adhere to the canonical schemas defined in `v13.libs.canonical`.

## 2. Invariants

- **Zero-Simulation**: All economic events must be cryptographically verified before persistence.
- **Canonical Types**: No ad-hoc dictionaries; use `UserIdentity`, `ContentMetadata`, etc.
- **PQC Enforcement**: Critical actions require PQC signatures.

## 3. Data Models

Reference `v13.libs.canonical.models` for full schema definitions.

### 3.1 Identity

- `UserIdentity`: Used for session hydration and profile display.
- **Source of Truth**: QFS Ledger (Wallet Address).

### 3.2 Content

- `ContentMetadata`: Header for all user-generated content (posts, comments).
- **Storage**: IPFS (Payload) + QFS (Metadata/Hash).

### 3.3 Economics

- `EconomicEvent`: Used for displaying transaction history and wallet balances.
- **Precision**: `amount` is strictly a string representation of `BigNum128`.

## 4. Endpoints (Conceptual)

### `POST /api/v1/content/publish`

- **Input**: `ContentMetadata` (with signed payload hash)
- **Output**: `EconomicEvent` (Reward result)

### `GET /api/v1/user/{user_id}/balance`

- **Output**: List[`EconomicEvent`]
