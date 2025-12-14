# StorageEngine Interface Spec (Authoritative, Language-Agnostic)

## Scope

This spec defines the **authoritative** interface and determinism requirements for StorageEngine, independent of language/runtime.

It is designed to guarantee:
- deterministic replay from StorageEvents/EQM
- bounded, enumerated error semantics
- zero-simulation compliance for consensus-visible behavior

## Versioning

- **Spec Version**: 1.0
- **Hash Function**: `SHA3-256`
- **Canonical JSON**: `sort_keys=true`, separators `(',', ':')`, UTF-8

## Constants (protocol-governed)

- `BLOCK_SIZE_BYTES` (default 262144)
- `REPLICATION_FACTOR` (default 3)
- `NUM_SHARDS_PER_OBJECT` (default 4)

All constants are treated as **governed configuration** and must be recorded in replay context.

---

## Data model

### StorageObjectIdentity

- `object_id: string`
  - deterministic identifier (content-addressed or namespace-hash)

### StorageObjectVersion

- `version: uint64`
  - monotonic, append-only

### StorageCommit

- `hash_commit: string`
  - hex SHA3-256
  - computed as:

```
hash_commit = SHA3-256( content_bytes || schema_version || canonical_json(metadata_seed) )
```

### ShardIdentity

- `shard_id: string`
  - hex SHA3-256
  - computed as:

```
shard_id = SHA3-256( f"{object_id}:{version}:{shard_index}" )
```

---

## Public interface

### 1) store

**Purpose**: deterministically store content bytes (ciphertext) with sharding and replication assignment.

**Request**
```json
{
  "object_id": "string",
  "version": 1,
  "content_bytes": "bytes",
  "metadata": {"any": "json"},
  "timestamp_tick": 0,
  "epoch": 0
}
```

**Response (success)**
```json
{
  "ok": true,
  "hash_commit": "hex",
  "shard_ids": ["hex"],
  "replica_sets": {
    "<shard_id>": ["node_id_a", "node_id_b", "node_id_c"]
  },
  "atr_cost": "decimal-string",
  "storage_event_id": "hex"
}
```

**Determinism constraints**
- shard_ids and replica sets depend only on:
  - canonical request content
  - governed constants
  - eligible_nodes(epoch)
- no wall-clock, randomness, or per-node heuristics

### 2) read

**Purpose**: deterministically reconstruct full content bytes for (object_id, version) from shards.

**Request**
```json
{
  "object_id": "string",
  "version": 1
}
```

**Response (success)**
```json
{
  "ok": true,
  "content_bytes": "bytes",
  "hash_commit": "hex",
  "proofs": ["proof"],
  "storage_event_id": "hex"
}
```

**Determinism constraints**
- content reconstruction must be ordered deterministically by shard_index

### 3) get_proof

**Purpose**: return deterministic proof material for a shard.

**Request**
```json
{
  "object_id": "string",
  "version": 1,
  "shard_id": "hex"
}
```

**Response (success)**
```json
{
  "ok": true,
  "merkle_root": "hex",
  "proof": "proof",
  "assigned_nodes": ["node_id"],
  "storage_event_id": "hex"
}
```

### 4) list_objects

**Purpose**: deterministic listing for observability and audit.

**Request**
```json
{
  "filters": {"any": "json"}
}
```

**Response (success)**
```json
{
  "ok": true,
  "objects": [
    {
      "object_id": "string",
      "version": 1,
      "hash_commit": "hex",
      "created_at_tick": 0,
      "metadata": {"any": "json"}
    }
  ],
  "storage_event_id": "hex"
}
```

**Determinism constraints**
- sort order MUST be `(object_id, version)`

---

## Management interface (epoch + nodes)

### 5) register_node

```json
{
  "node_id": "string",
  "host": "string",
  "port": 0
}
```

**Response**
```json
{ "ok": true, "storage_event_id": "hex" }
```

### 6) advance_epoch

```json
{
  "epoch": 1,
  "aegis_registry_snapshot": {"any": "json"},
  "aegis_telemetry_snapshot": {"any": "json"}
}
```

**Response**
```json
{ "ok": true, "storage_event_id": "hex" }
```

---

## StorageEvent (EQM) schema (required for replay)

Every public call MUST emit exactly one StorageEvent with deterministic fields.

```json
{
  "event_id": "hex",
  "event_type": "STORE|READ|GET_PROOF|LIST_OBJECTS|NODE_REGISTRATION|NODE_STATUS|EPOCH_ADVANCEMENT",
  "epoch": 0,
  "timestamp_tick": 0,

  "object_id": "string",
  "version": 1,
  "hash_commit": "hex",

  "content_size": 123,
  "shard_ids": ["hex"],
  "replica_sets": {"<shard_id>": ["node_id"]},

  "atr_cost": "decimal-string",
  "pqc_signature": "optional-hex",

  "error_code": "optional",
  "error_detail": "optional"
}
```

**Replay rule:** Given ordered StorageEvents + governed constants, a replay engine must reconstruct:
- objects/shards
- placement / replica sets
- per-node bytes stored + proofs verified + uptime buckets (derived from epoch snapshots)

---

## Error model (finite, enumerated)

Errors must be mapped into this bounded set:

- `SE_ERR_NOT_FOUND`
- `SE_ERR_INVALID_VERSION`
- `SE_ERR_INVALID_INPUT`
- `SE_ERR_NO_ELIGIBLE_NODES`
- `SE_ERR_PROOF_UNAVAILABLE`
- `SE_ERR_INTEGRITY_MISMATCH`
- `SE_ERR_AEGIS_CONTEXT_MISSING`
- `SE_ERR_INTERNAL`

**Rule:** Internal exceptions are not exposed directly; they are mapped to `SE_ERR_INTERNAL` with a safe `error_detail`.

---

## Notes on current implementation alignment

- Current Python implementation uses:
  - `put_content`, `get_content`, `get_storage_proof`, `list_objects`
  - deterministic hashing and deterministic node assignment
  - `storage_event_log` exists but must be upgraded to the full StorageEvent schema above.
