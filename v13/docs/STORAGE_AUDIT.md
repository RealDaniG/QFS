# ATLAS V13.8 Storage Audit Guide

## Overview

This document describes how to independently verify the integrity of content stored in the QFS-V13 Decentralized Storage Network using the "Explain-This" audit trails and cryptographic proofs.

## Verification Scope

1. **Content Integrity:** Ensuring the file has not been tampered with (SHA3-256 Hash).
2. **Storage Proofs:** Ensuring shards are correctly stored and possess valid Merkle Proofs.
3. **Placement Policy:** Ensuring content is replicated across the required number of AEGIS-verified nodes (RF=3).
4. **Zero-Simulation:** Ensuring all proofs and placements are deterministic consequences of the ledger state.

## 1. Verifying Content Integrity

The `hash_commit` in the `LogEntry` or `Explanation` is the SHA3-256 hash of:
`content_bytes + schema_version + deterministic_metadata_json`

To verify:

1. Download the content.
2. Retrieve the metadata used at storage time.
3. Compute the hash using the standard QFS algorithm (`v13.core.StorageEngine._compute_content_hash`).
4. Compare with the Ledger's `hash_commit`.

## 2. Verifying Storage Proofs

Fetch the Storage Explanation via API:

```bash
GET /api/v1/explain/storage/{content_id}
```

Response includes `proof_outcomes`. Each successful proof verifies that a node possesses the correct data shard.

### Manual Merkle Verification

If you have the raw shard data, you can verify the Merkle Root:

1. Split shard content into 4KB blocks.
2. Hash each block (SHA3-256).
3. Construct the Merkle Tree.
4. Compare the Root with the one provided in the `PROOF_GENERATED` event.

## 3. Verifying Placement Policy (AEGIS)

The system enforces `Replication Factor = 3`.

The API response lists `assigned_nodes`.
To audit compliance:

1. Check that `len(assigned_nodes) >= 3`.
2. (Advanced) Cross-reference node IDs with the `AEGIS_REGISTRY` snapshot for the `epoch_assigned` to ensure they were `Active` and `Verified`.

## 4. Disaster Recovery & Replay

To rebuild the state from scratch:

1. Set `EXPLAIN_THIS_SOURCE=live_ledger`.
2. Point `QFS_LEDGER_PATH` to your immutable ledger artifact.
3. Run the Replay Engine.

The engine will reconstruct the exact placement map deterministically. Any deviation indicates software drift or ledger corruption.
