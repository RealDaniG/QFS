# QFS V13.x Decentralized Storage Specification

## 1. Objectives & Hard Constraints

- Replace centralized PostgreSQL as the primary content store with a **decentralized, node‑based, content‑addressed storage layer** that is fully compatible with QFS, ATLAS, AEGIS, and OpenAGI.
- Preserve **Zero‑Simulation**, **determinism**, **replayability**, and **auditability**; all storage behavior must be reproducible from logs and deterministic formulas.
- Keep NOD strictly **infrastructure‑only** and preserve user privacy by ensuring raw content never leaves its hosting nodes.

### 1.1 Invariants

- **Content‑addressed & shard‑based**:
  - Every logical content object has a deterministic `object_id` and `hash_commit = H(content_bytes || schema_version || metadata_seed)` specified at the QFS protocol level.
  - Storage is sharded: `shard_id = H(object_id || shard_index)` with a fixed, documented hash function (e.g., SHA3‑256, QFS standard).

- **Zero‑Simulation compliance**:
  - Node selection, placement, replication, and NOD rewards rely only on deterministic formulas using CertifiedMath/BigNum128 and sorted data structures.
  - No random seeding, no nondeterministic ordering, no "fastest node wins".

- **Replayable history**:
  - Content is **append‑only and versioned**: `object_id → {version, hash_commit, metadata}` list.
  - Historical states can be reconstructed by replaying EQM logs and storage events.

## 2. Architecture – Detailed Design

### 2.1 Storage Nodes & API

Each storage node is an AEGIS‑verified node that exposes a minimal, deterministic API:

- `write(object_id, version, content_chunk, metadata) -> {hash_commit, shard_ids[]}`
- `read(object_id, version) -> {content_chunk, hash_commit, proof}`
- `get_proof(object_id, version, shard_id) -> Merkle/proof_of_storage`
- `list_objects(filter) -> deterministic, sorted list of object summaries`

**Telemetry:**

- Each node emits telemetry (uptime, failures, latency bands) to AEGIS **as observations only**.
- Telemetry is logged and used for monitoring and governance, but **cannot affect live placement or reward calculations** except via pre‑defined, deterministic formulas that use aggregated, epoch‑level metrics.

### 2.2 Data Model

At the protocol level (QFS/ATLAS):

- **Logical object**:
  - `object_id` (deterministic, e.g., hash of client‑side ID + namespace).
  - `version` (monotonic integer or logical clock).
  - `hash_commit` (content + schema + metadata seed hash).
  - `metadata`:
    - `author_node_id`
    - `created_at_tick` (DeterministicTime, not wall‑clock)
    - `tags` (normalized, deterministic order)
    - `openagi_score` (deterministic scalar per scoring model)
    - `atr_fee_events` (compact references to ATR debits/credits)
    - `aegis_telemetry_stub` (node_id, proof_result, latency_band, at_epoch)

- **Sharding**:
  - `shard_id = H(object_id || version || shard_index)`; shard indices and counts are fixed by protocol (e.g., `NUM_SHARDS_PER_OBJECT = 4` configurable by governance).
  - Nodes are selected from an **eligible node list** sorted by `node_id` and filtered by governance rules.

### 2.3 Deterministic Replication & NOD Incentives

- **Node selection for each shard**:
  - Let `eligible_nodes` be a sorted list of node_ids that passed AEGIS verification for the epoch.
  - For each `shard_id`, select nodes via:
    - `start_index = H(shard_id) mod len(eligible_nodes)`
    - Select `REPLICATION_FACTOR` consecutive nodes modulo the list length.
  - All computation uses CertifiedMath/BigNum128 to avoid float drift.

- **NOD rewards**:
  - For each epoch:
    - Compute storage contribution metrics per node:
      - `bytes_stored` (deterministic count from EQM logs).
      - `uptime_bucket` (derived from AEGIS telemetry with deterministic aggregation rules).
      - `successful_proofs` (count of verified `get_proof` events).
    - Apply a deterministic NOD reward formula:
      - `NOD_reward[node] = f(bytes_stored, uptime_bucket, successful_proofs)` using only CertifiedMath.
  - Final NOD reward allocations are logged in TokenStateBundle and recorded as ledger events.

## 3. Integration with QFS, AEGIS, ATLAS, OpenAGI

### 3.1 QFS & TokenStateBundle

- **ATR fees for storage**:
  - Each `write` action carries a deterministic ATR fee event (defined per object size, complexity, and policy).
  - ATR debits and any FLX/NOD distributions are computed in TreasuryEngine and written into TokenStateBundle alongside storage metrics.

- **Storage contribution tracking**:
  - TokenStateBundle is extended with:
    - `storage_bytes_stored[node]`
    - `storage_uptime_bucket[node]`
    - `storage_proofs_verified[node]`

### 3.2 AEGIS Telemetry

- AEGIS node registration and verification:
  - Only nodes with valid AEGIS snapshots are eligible for `eligible_nodes`.
  - AEGIS telemetry (sub‑second latencies, error rates) is aggregated per epoch and recorded in EQM logs.

- Telemetry is **non‑authoritative** for economics:
  - It influences eligible node lists only via explicit governance rules (e.g., "nodes with uptime below X% are excluded next epoch").
  - No per‑request "fastest node" decisions.

### 3.3 OpenAGI Integration

- OpenAGI performs content analysis/scoring **node‑locally**:
  - Uses encrypted embeddings or ephemeral decrypted views **within node trust boundary**; raw content never leaves nodes.
  - Scoring outputs deterministic, bounded scalars (e.g., `score ∈ [0, 1_000_000]`) recorded in `metadata.openagi_score`.

- OpenAGI never writes to ledger directly:
  - It emits recommendations or metadata updates via QFS SDK; all effects on economics flow through TreasuryEngine and PolicyRegistry.

## 4. Constants

### 4.1 Storage Constants

```python
# Block/chunk size in bytes
BLOCK_SIZE_BYTES = 262144  # 256 KiB

# Number of shards per object
NUM_SHARDS_PER_OBJECT = 4

# Replication factor
REPLICATION_FACTOR = 3

# Hash function for content addressing
CONTENT_HASH_FUNCTION = "SHA3-256"

# Hash function for shard ID calculation
SHARD_HASH_FUNCTION = "SHA3-256"
```

### 4.2 Deterministic Formulas

1. **Content Hash Calculation**:
   ```
   hash_commit = H(content_bytes || schema_version || metadata_seed)
   ```

2. **Shard ID Calculation**:
   ```
   shard_id = H(object_id || version || shard_index)
   ```

3. **Node Selection**:
   ```
   eligible_nodes = SORT(AEGIS_verified_nodes)
   start_index = H(shard_id) mod len(eligible_nodes)
   selected_nodes = [eligible_nodes[(start_index + i) mod len(eligible_nodes)] 
                     for i in range(REPLICATION_FACTOR)]
   ```

4. **NOD Reward Formula**:
   ```
   NOD_reward[node] = f(bytes_stored, uptime_bucket, successful_proofs)
   ```

## 5. StorageEngine Interface

```python
class StorageEngine:
    """
    Deterministic storage engine implementing the decentralized storage protocol.
    """
    
    def put_content(self, object_id: str, version: int, content: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store content with deterministic sharding and replication.
        
        Args:
            object_id: Deterministic object identifier
            version: Monotonic version number
            content: Content bytes to store
            metadata: Associated metadata
            
        Returns:
            Dict with hash_commit and shard_ids
        """
        pass
    
    def get_content(self, object_id: str, version: int) -> Dict[str, Any]:
        """
        Retrieve content with proof verification.
        
        Args:
            object_id: Object identifier
            version: Version number
            
        Returns:
            Dict with content_chunk, hash_commit, and proof
        """
        pass
    
    def get_storage_proof(self, object_id: str, version: int, shard_id: str) -> Dict[str, Any]:
        """
        Get Merkle proof of storage for a specific shard.
        
        Args:
            object_id: Object identifier
            version: Version number
            shard_id: Shard identifier
            
        Returns:
            Merkle proof of storage
        """
        pass
    
    def list_objects(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        List objects with deterministic sorting.
        
        Args:
            filters: Filter criteria
            
        Returns:
            Sorted list of object summaries
        """
        pass
```

## 6. Integration Points

### 6.1 AtlasAPIGateway Integration

The AtlasAPIGateway will integrate with the StorageEngine through:

1. **Storage Client Injection**:
   ```python
   def set_storage_engine(self, storage_engine: StorageEngine) -> None:
       """Set the storage engine for content operations."""
   ```

2. **Content Operations**:
   - Feed content retrieval
   - User content publishing
   - Content metadata queries

### 6.2 AEGIS Integration

Storage nodes must register with AEGIS and pass verification:

1. **Node Registration**:
   ```python
   def register_storage_node(self, node_info: Dict[str, Any]) -> bool:
       """Register storage node with AEGIS verification."""
   ```

2. **Eligibility Management**:
   ```python
   def get_eligible_nodes(self) -> List[str]:
       """Get list of AEGIS-verified storage nodes."""
   ```

### 6.3 TokenStateBundle Extension

Extend TokenStateBundle with storage metrics:

```python
class TokenStateBundle:
    # ... existing fields ...
    
    # Storage contribution metrics
    storage_bytes_stored: Dict[str, BigNum128]  # node_id -> bytes
    storage_uptime_bucket: Dict[str, int]       # node_id -> bucket
    storage_proofs_verified: Dict[str, int]     # node_id -> count
```

## 7. Security & Compliance

### 7.1 End-to-End Encryption

- Client-side key management
- StorageEngine only stores ciphertext
- EQM logs never contain raw content, only hashes and metadata

### 7.2 Sybil Resistance

- Only AEGIS-verified nodes join the storage set
- Governance can quarantine or expel nodes with repeated failures

### 7.3 Audit Log

Every store/update/delete-marker emits an EQM entry:
- `event_type` (STORE/UPDATE/DELETE_MARKER)
- `object_id`, `version`, `hash_commit`
- `node_set` (assigned nodes)
- `pqc_signature` and CRS chain linkage

### 7.4 Privacy

- OpenAGI and any external agents see only metadata and hashed IDs
- No global index of raw content; all search/analysis uses hashed IDs or encrypted embeddings

## 8. Evidence Artifacts

This specification requires the following evidence artifacts:

1. `evidence/storage/storage_determinism.json` - Verification of deterministic behavior
2. `evidence/storage/storage_economics.json` - Verification of NOD reward calculations
3. `evidence/storage/storage_replay.json` - Verification of replayability from logs
4. `PHASE_STORAGE_EVIDENCE.md` - Complete audit mapping of guarantees to tests and artifacts

## 9. Implementation Roadmap

This specification will be implemented through the following phases:

1. **Phase 0**: Spec & Freeze (Complete)
2. **Phase 1**: StorageEngine Stub & Mini-Network
3. **Phase 2**: AEGIS Integration
4. **Phase 3**: OpenAGI & ATR/NOD Wiring
5. **Phase 4**: Dual-Write & Consistency
6. **Phase 5**: Cutover & Stabilization