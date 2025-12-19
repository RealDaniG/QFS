# Proof-of-Execution (PoE) Schema v1.0

> **Version:** 1.0  
> **Status:** CANONICAL  
> **Last Updated:** December 19, 2025

## Overview

This document defines the canonical schema for QFS × ATLAS Proof-of-Execution (PoE) artifacts. All governance execution proofs MUST conform to this schema.

## Design Principles

1. **Versioned:** Schema includes version field for evolution
2. **Complete:** All information needed for independent verification
3. **Deterministic:** Schema supports bit-for-bit replay
4. **Signed:** Cryptographically bound to executor identity
5. **Composable:** Artifacts can be chained and indexed

## Schema Definition

### Canonical Format

**Primary:** JSON  
**Optional:** YAML (for human readability)

### Mandatory Fields

```json
{
  "poe_version": "1.0",
  "artifact_id": "string",
  "proposal_hash": "string",
  "governance_scope": {
    "epoch": "integer",
    "cycle": "integer",
    "parameter_key": "string"
  },
  "execution_phase": "string",
  "before_state_hash": "string",
  "after_state_hash": "string",
  "vote_breakdown": {
    "total_stake": "integer",
    "yes_stake": "integer",
    "no_stake": "integer",
    "quorum_met": "boolean",
    "supermajority_met": "boolean"
  },
  "execution_trace_hash": "string",
  "proof_hash": "string",
  "signatures": {
    "nod_address": "string",
    "dilithium_signature": "string",
    "signature_timestamp": "string"
  },
  "runtime_info": {
    "code_commit_hash": "string",
    "build_hash": "string",
    "deterministic_session_timestamp_hash": "string",
    "python_version": "string",
    "certifiedmath_version": "string"
  },
  "replay_instructions": {
    "command": "string",
    "inputs_file": "string",
    "expected_output_hash": "string"
  }
}
```

## Field Specifications

### poe_version

- **Type:** String (semantic version)
- **Format:** `"MAJOR.MINOR"`
- **Example:** `"1.0"`
- **Purpose:** Schema version for compatibility checking

### artifact_id

- **Type:** String
- **Format:** `"GOV-{epoch}-{phase}-{sequence}"`
- **Example:** `"GOV-148-EXEC-02"`
- **Purpose:** Unique identifier for this PoE artifact

### proposal_hash

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:a3f5b2c1d4e6f7a8..."`
- **Purpose:** Content-addressed proposal identifier

### governance_scope

Object containing governance context:

**epoch:**

- **Type:** Integer
- **Example:** `148`
- **Purpose:** Governance epoch number

**cycle:**

- **Type:** Integer
- **Example:** `2`
- **Purpose:** Cycle within epoch

**parameter_key:**

- **Type:** String
- **Example:** `"VIRAL_POOL_CAP"`
- **Purpose:** Parameter being changed

### execution_phase

- **Type:** String (enum)
- **Values:** `"PROPOSAL"`, `"VOTE"`, `"COOLDOWN"`, `"EXECUTION"`
- **Example:** `"EXECUTION"`
- **Purpose:** Governance phase this PoE represents

### before_state_hash

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:b4c6d8e2f0a1b3c5..."`
- **Purpose:** State hash before execution

### after_state_hash

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:c5d7e9f3a1b4c6d8..."`
- **Purpose:** State hash after execution

### vote_breakdown

Object containing voting results:

**total_stake:**

- **Type:** Integer
- **Example:** `10000`
- **Purpose:** Total stake that voted

**yes_stake:**

- **Type:** Integer
- **Example:** `7500`
- **Purpose:** Stake voting YES

**no_stake:**

- **Type:** Integer
- **Example:** `2500`
- **Purpose:** Stake voting NO

**quorum_met:**

- **Type:** Boolean
- **Example:** `true`
- **Purpose:** Whether quorum threshold (30%) was met

**supermajority_met:**

- **Type:** Boolean
- **Example:** `true`
- **Purpose:** Whether supermajority threshold (66%) was met

### execution_trace_hash

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:d6e8f0a4b2c6d8e0..."`
- **Purpose:** Hash of execution trace (operations performed)

### proof_hash

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:e7f9a1b5c3d7e9f1..."`
- **Purpose:** Final proof hash (hash of all above fields)

### signatures

Object containing cryptographic signatures:

**nod_address:**

- **Type:** String
- **Format:** `"NOD_0x{hex}"`
- **Example:** `"NOD_0x1234567890abcdef..."`
- **Purpose:** NOD operator address

**dilithium_signature:**

- **Type:** String
- **Format:** `"base64:{signature}"`
- **Example:** `"base64:AQIDBAUG..."`
- **Purpose:** CRYSTALS-Dilithium signature over proof_hash

**signature_timestamp:**

- **Type:** String (ISO 8601)
- **Format:** `"YYYY-MM-DDTHH:MM:SSZ"`
- **Example:** `"2025-12-19T14:00:00Z"`
- **Purpose:** When signature was created

### runtime_info

Object containing runtime environment:

**code_commit_hash:**

- **Type:** String
- **Example:** `"a3f5b2c1"`
- **Purpose:** Git commit hash of code

**build_hash:**

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:f8a0b2c6d4e8f0a2..."`
- **Purpose:** Hash of built artifacts

**deterministic_session_timestamp_hash:**

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:g9b1c3d7e5f9a1b3..."`
- **Purpose:** Session timestamp hash for replay

**python_version:**

- **Type:** String
- **Example:** `"3.11.7"`
- **Purpose:** Python version used

**certifiedmath_version:**

- **Type:** String
- **Example:** `"1.0.0"`
- **Purpose:** CertifiedMath library version

### replay_instructions

Object containing replay information:

**command:**

- **Type:** String
- **Example:** `"python replay_gov_cycle.py --artifact_id GOV-148-EXEC-02"`
- **Purpose:** Command to replay this execution

**inputs_file:**

- **Type:** String
- **Example:** `"evidence/GOV-148-EXEC-02-inputs.json"`
- **Purpose:** Path to replay inputs

**expected_output_hash:**

- **Type:** String
- **Format:** `"sha3_512:{hex}"`
- **Example:** `"sha3_512:e7f9a1b5c3d7e9f1..."`
- **Purpose:** Expected output hash for verification

## Example Artifact

```json
{
  "poe_version": "1.0",
  "artifact_id": "GOV-148-EXEC-02",
  "proposal_hash": "sha3_512:a3f5b2c1d4e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
  "governance_scope": {
    "epoch": 148,
    "cycle": 2,
    "parameter_key": "VIRAL_POOL_CAP"
  },
  "execution_phase": "EXECUTION",
  "before_state_hash": "sha3_512:b4c6d8e2f0a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3",
  "after_state_hash": "sha3_512:c5d7e9f3a1b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6",
  "vote_breakdown": {
    "total_stake": 10000,
    "yes_stake": 7500,
    "no_stake": 2500,
    "quorum_met": true,
    "supermajority_met": true
  },
  "execution_trace_hash": "sha3_512:d6e8f0a4b2c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8",
  "proof_hash": "sha3_512:e7f9a1b5c3d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9",
  "signatures": {
    "nod_address": "NOD_0x1234567890abcdef1234567890abcdef12345678",
    "dilithium_signature": "base64:AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+fw==",
    "signature_timestamp": "2025-12-19T14:00:00Z"
  },
  "runtime_info": {
    "code_commit_hash": "a3f5b2c1",
    "build_hash": "sha3_512:f8a0b2c6d4e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0",
    "deterministic_session_timestamp_hash": "sha3_512:g9b1c3d7e5f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1",
    "python_version": "3.11.7",
    "certifiedmath_version": "1.0.0"
  },
  "replay_instructions": {
    "command": "python replay_gov_cycle.py --artifact_id GOV-148-EXEC-02",
    "inputs_file": "evidence/GOV-148-EXEC-02-inputs.json",
    "expected_output_hash": "sha3_512:e7f9a1b5c3d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9"
  }
}
```

## Validation Rules

### Schema Compliance

- All mandatory fields MUST be present
- Field types MUST match specification
- Hash formats MUST be `"sha3_512:{hex}"`
- Timestamps MUST be ISO 8601 UTC

### Cryptographic Integrity

- `proof_hash` MUST be SHA3-512 of all fields (excluding signatures)
- `dilithium_signature` MUST verify against `proof_hash`
- All hashes MUST be 128 hex characters (512 bits)

### Governance Validity

- `quorum_met` MUST be true if `total_stake >= 30% of eligible stake`
- `supermajority_met` MUST be true if `yes_stake >= 66% of total_stake`
- `execution_phase` MUST be valid enum value

### Replay Validity

- `replay_instructions.command` MUST be executable
- `replay_instructions.inputs_file` MUST exist
- Replay output hash MUST match `expected_output_hash`

## Versioning

### Current Version: 1.0

**Breaking Changes (Major Version):**

- Removing mandatory fields
- Changing field types
- Changing hash algorithms

**Non-Breaking Changes (Minor Version):**

- Adding optional fields
- Adding enum values
- Documentation updates

### Backward Compatibility

**Guarantee:** All v1.x artifacts will remain valid and verifiable.

**Forward Compatibility:** Parsers MUST ignore unknown fields in v1.x.

## Security Considerations

### Signature Verification

1. Extract `proof_hash` from artifact
2. Verify `dilithium_signature` against `proof_hash`
3. Confirm `nod_address` is authorized
4. Check `signature_timestamp` is recent

### Replay Verification

1. Load artifact and inputs
2. Execute replay command
3. Compare output hash to `expected_output_hash`
4. Verify `after_state_hash` matches

### Forgery Resistance

**To forge a PoE artifact, attacker must:**

1. Break SHA3-512 (find collision)
2. Break CRYSTALS-Dilithium (forge signature)
3. Break deterministic execution (create drift)

**Classified as:** Computationally infeasible under post-quantum assumptions.

## Usage

### Generating PoE Artifacts

```python
from v15.atlas.governance import ProposalEngine

engine = ProposalEngine(registry)
proposal_id = "..."

# Execute proposal (automatically generates PoE)
engine.execute_proposal(proposal_id)

# Retrieve PoE artifact
poe_artifact = engine.get_poe_artifact(proposal_id)
```

### Verifying PoE Artifacts

```python
from v15.tools import verify_poe

# Load artifact
artifact = load_poe_artifact("GOV-148-EXEC-02.json")

# Verify signature
signature_valid = verify_poe.verify_signature(artifact)

# Verify replay
replay_valid = verify_poe.verify_replay(artifact)

# Overall validity
if signature_valid and replay_valid:
    print("✓ PoE artifact is valid")
```

## References

- [v15.3 PoE Integration Plan](../implementation_plan.md)
- [HOW_TO_AUDIT_QFS_V15.md](HOW_TO_AUDIT_QFS_V15.md)
- [SECURITY_ASSUMPTIONS.md](SECURITY_ASSUMPTIONS.md)

---

**This schema is the canonical contract for all QFS × ATLAS governance execution proofs.**
