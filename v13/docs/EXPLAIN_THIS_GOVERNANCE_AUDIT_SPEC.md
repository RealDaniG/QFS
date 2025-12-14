# Explain-This Governance Audit Specification (V13.8)

## Overview

This specification defines the cryptographic and operational requirements for the "Governance Audit" slice of Explain-This. It ensures that all system actions (contract upgrades, policy changes, signal registration) are immutable, verifiable, and transparent to AEGIS.

## Core Invariants

1. **Immutable Chaining**: All audit logs must strictly reference the hash of the previous log entry.
2. **Deterministic Serialization**: JSON serialization for hashing must use `sort_keys=True` and strict separators.
3. **AEGIS Verification**: Every critical governance action must include a verifiable DID signature from an authorized actor.
4. **Zero-Simulation**: Audit logs must be persisted in the Coherence Ledger, not in sidecar databases or logs.

## Data Structures

### AuditLogEntry

```json
{
  "id": "uuid",
  "prev_hash": "sha256...",
  "timestamp": "ISO8601",
  "type": "CONTRACT | SIGNAL | REWARD | STORAGE",
  "actor_did": "did:key:...",
  "action": "string description",
  "payload_hash": "sha256...",
  "hash": "sha256(self - hash)"
}
```

## API Endpoints

### `GET /governance/audit-log`

- **Purpose**: Retrieve verified audit trail.
- **Parameters**: `limit`, `type`, `start_time`
- **Response**: List of `AuditLogEntry`
- **Verification**: Client must verify `prev_hash` chain continuity.

## Integration

- **Frontend**: `GovernanceAuditDashboard` visualizes the chain and highlights breaks.
- **Backend**: `audit_integrity.py` provides shared verification logic.
- **Ledger**: `CoherenceLedger` is the source of truth.

## Security

- **Tamper Evidence**: Any modification to a log entry breaks the hash chain.
- **Non-Repudiation**: Actor DIDs enforce accountability.
