# ATLAS x QFS: Event Ledger Protocol Specification

**Version**: 1.0.0  
**Status**: Draft  
**Last Updated**: December 13, 2025

---

## 1. Overview

The Event Ledger is the append-only, hash-linked, cryptographically verifiable source of truth for all state transitions in the ATLAS x QFS network. It provides immutable auditability, deterministic replay, and serves as the foundation for distributed consensus.

### Design Goals

- **Immutability**: Events cannot be modified or deleted once written
- **Verifiability**: Any party can verify event integrity via hash chains and signatures
- **Determinism**: Same event stream always produces same final state
- **Decentralization**: No single authority controls the ledger
- **Efficiency**: Support for light clients and efficient queries

---

## 2. Event Structure

### 2.1 Base Event Schema

All events MUST conform to this schema:

```typescript
interface LedgerEvent {
  // Core identifiers
  event_id: string;           // UUID v4 or event-specific format
  event_type: EventType;      // Enumerated event type
  timestamp: number;          // Unix timestamp (milliseconds)
  sequence_number: number;    // Monotonically increasing per ledger partition
  
  // Content
  actor: string;              // DID of the entity initiating the event
  modules: string[];          // List of modules involved (e.g., ["QFS", "SafetyGuard"])
  inputs: EventInputs;        // Event-specific inputs (hashed if sensitive)
  outcome: EventOutcome;      // Result of the event
  
  // Governance & Policy
  policy_version: string;     // Version of active policy (e.g., "v1.2.3")
  guards_evaluated?: GuardResult[];  // Optional: guard evaluation results
  
  // Explainability
  explanation: string;        // Human-readable explanation
  metadata?: Record<string, unknown>;  // Optional additional context
  
  // Cryptographic integrity
  previous_event_hash: string;  // SHA-256 hash of previous event (for hash-linking)
  event_hash: string;           // SHA-256 hash of this event (excluding this field)
  signature: string;            // Ed25519 or post-quantum signature
  signer_did: string;           // DID of the signing entity (node, user, contract)
}
```

### 2.2 Event Types

Events are categorized by domain:

```typescript
enum EventType {
  // Content & Interaction
  ContentCreated = "ContentCreated",
  ContentUpdated = "ContentUpdated",
  ContentDeleted = "ContentDeleted",  // Soft delete, content CID remains
  InteractionCreated = "InteractionCreated",  // Like, comment, repost
  
  // Social Graph
  Follow = "Follow",
  Unfollow = "Unfollow",
  Block = "Block",
  Unblock = "Unblock",
  
  // Communities
  CommunityCreated = "CommunityCreated",
  CommunityUpdated = "CommunityUpdated",
  CommunityJoined = "CommunityJoined",
  CommunityLeft = "CommunityLeft",
  
  // Economic
  RewardAllocated = "RewardAllocated",
  RewardClaimed = "RewardClaimed",
  PenaltyApplied = "PenaltyApplied",
  TokenTransfer = "TokenTransfer",
  
  // QFS Computation
  FeedComputed = "FeedComputed",
  CoherenceScored = "CoherenceScored",
  ReputationUpdated = "ReputationUpdated",
  
  // Guards & Safety
  GuardEvaluated = "GuardEvaluated",
  GuardFailed = "GuardFailed",
  AEGISVeto = "AEGISVeto",
  AEGISRollback = "AEGISRollback",
  
  // Moderation
  ModerationAction = "ModerationAction",
  AppealSubmitted = "AppealSubmitted",
  AppealReviewed = "AppealReviewed",
  AppealResolved = "AppealResolved",
  
  // Governance
  PolicyProposed = "PolicyProposed",
  PolicyVoted = "PolicyVoted",
  PolicyActivated = "PolicyActivated",
  PolicyDeactivated = "PolicyDeactivated",
  
  // OPEN-AGI
  AGIObservation = "AGIObservation",
  AGIRecommendation = "AGIRecommendation",
  AGISimulation = "AGISimulation",
  
  // Infrastructure
  NodeRegistered = "NodeRegistered",
  NodeDeregistered = "NodeDeregistered",
  NodeAvailabilityReport = "NodeAvailabilityReport",
  ComputationDispute = "ComputationDispute",
  
  // Identity
  ProfileCreated = "ProfileCreated",
  ProfileUpdated = "ProfileUpdated",
  DIDAuthenticated = "DIDAuthenticated",
}
```

---

## 3. Hash-Linking Protocol

### 3.1 Event Hash Calculation

```typescript
function calculateEventHash(event: Omit<LedgerEvent, 'event_hash' | 'signature'>): string {
  // 1. Serialize to canonical JSON (sorted keys, no whitespace)
  const canonical = canonicalJSON(event);
  
  // 2. Compute SHA-256
  return SHA256(canonical);
}
```

### 3.2 Hash Chain Verification

Each event links to the previous event via `previous_event_hash`:

```
Event 0 (Genesis): previous_event_hash = "0x0000...0000"
Event 1: previous_event_hash = hash(Event 0)
Event 2: previous_event_hash = hash(Event 1)
...
```

**Verification Algorithm**:

```typescript
function verifyHashChain(events: LedgerEvent[]): boolean {
  for (let i = 1; i < events.length; i++) {
    const expected = calculateEventHash(events[i - 1]);
    if (events[i].previous_event_hash !== expected) {
      return false;
    }
  }
  return true;
}
```

---

## 4. Signatures & Authentication

### 4.1 Signature Scheme

- **Primary**: Ed25519 (for efficiency)
- **Post-Quantum**: Dilithium or Falcon (for future-proofing)

### 4.2 Signing Process

```typescript
function signEvent(event: Omit<LedgerEvent, 'signature'>, privateKey: PrivateKey): string {
  // 1. Calculate event hash
  const hash = calculateEventHash(event);
  
  // 2. Sign hash with private key
  return sign(hash, privateKey);
}
```

### 4.3 Verification Process

```typescript
function verifyEventSignature(event: LedgerEvent): boolean {
  // 1. Recalculate hash
  const hash = calculateEventHash(event);
  
  // 2. Resolve signer's DID to public key
  const publicKey = resolveDID(event.signer_did);
  
  // 3. Verify signature
  return verify(hash, event.signature, publicKey);
}
```

---

## 5. Merkle Batching for Scalability

### 5.1 Batch Structure

Events are grouped into batches (e.g., 1000 events per batch). Each batch has a Merkle root:

```typescript
interface EventBatch {
  batch_id: string;
  start_sequence: number;
  end_sequence: number;
  events: LedgerEvent[];
  merkle_root: string;
  batch_hash: string;
}
```

### 5.2 Merkle Tree Construction

```
         Root
        /    \
      H1      H2
     / \     / \
   H01 H02 H03 H04
   / \ / \ / \ / \
  E0 E1 E2 E3 E4 E5 E6 E7
```

### 5.3 Proofs for Light Clients

Light clients can verify an event without downloading the entire batch:

```typescript
interface MerkleProof {
  event: LedgerEvent;
  leaf_index: number;
  sibling_hashes: string[];  // Path from leaf to root
  batch_root: string;
}
```

---

## 6. Timestamp & Logical Clocks

### 6.1 Logical Timestamps

To ensure determinism, the ledger uses **logical clocks** (Lamport timestamps or vector clocks), not wall-clock timestamps.

```typescript
interface LogicalTimestamp {
  sequence_number: number;  // Monotonically increasing
  wall_clock_hint?: number; // Optional wall-clock time (not used for ordering)
}
```

### 6.2 Ordering Rule

Events are ordered by `sequence_number`. If multiple events have the same sequence number (in partitioned ledgers), use deterministic tie-breaking (e.g., lexicographic event_id order).

---

## 7. Schema Versioning

### 7.1 Version Field

All events include a `schema_version` field:

```typescript
interface LedgerEvent {
  schema_version: string;  // e.g., "1.0.0"
  // ...rest of fields
}
```

### 7.2 Migration Path

When schema changes:

1. **Minor version** (1.0.x → 1.1.x): Additive changes only (new optional fields)
2. **Major version** (1.x.x → 2.0.0): Breaking changes
   - Define migration function: `migrateV1toV2(event: V1Event): V2Event`
   - All nodes must support both versions during transition period

---

## 8. Access Patterns & APIs

### 8.1 Query Operations

**Get Event by ID**:

```
GET /ledger/events/{event_id}
```

**Query Events by Type**:

```
GET /ledger/events?type=ContentCreated&start_seq=1000&end_seq=2000
```

**Query Events by Actor**:

```
GET /ledger/events?actor=did:key:abc123&limit=100
```

**Stream Real-Time Events**:

```
WebSocket: ws://ledger-node/stream?since=12345
```

### 8.2 Write Operations

**Append Event** (only authorized entities):

```
POST /ledger/events
Body: {
  event: LedgerEvent,
  proof: AuthorizationProof
}
```

---

## 9. Partitioning for Scalability

### 9.1 Partition Strategy

Ledger can be partitioned by:

- **Object ID**: All events for a specific post/user/community in one partition
- **Time**: Events grouped by time range (e.g., daily partitions)
- **Event Type**: Separate partitions for Content vs. Economic vs. Governance events

### 9.2 Cross-Partition References

Events in one partition can reference events in another:

```typescript
interface CrossPartitionRef {
  partition_id: string;
  event_id: string;
  event_hash: string;
}
```

---

## 10. Export & Audit Format

### 10.1 Signed Bundle Format

For compliance and external audits:

```json
{
  "bundle_id": "audit-2025-12-13",
  "start_sequence": 1000,
  "end_sequence": 2000,
  "events": [ /* array of LedgerEvent */ ],
  "merkle_root": "0xabc123...",
  "bundle_signature": "...",
  "signer_did": "did:key:node1"
}
```

### 10.2 Verification

Auditors verify:

1. Hash chain integrity within bundle
2. Merkle root matches events
3. Bundle signature valid
4. Cross-reference with on-chain checkpoints (if applicable)

---

## 11. Security Considerations

### 11.1 Threat Model

**Threats**:

- Malicious node appending invalid events
- Node modifying past events
- Node censoring events
- Man-in-the-middle attacks on event propagation

**Mitigations**:

- Cryptographic signatures on every event
- Hash-linking prevents modification
- Replication across multiple nodes prevents censorship
- TLS for all network communication

### 11.2 Access Control

**Write Access**:

- Users: Can append events for their own actions (signed with their DID)
- Nodes: Can append computation results (QFS, guards)
- Smart Contracts: Can append governance events

**Read Access**:

- Public events: Anyone can read
- Private events: Encrypted, only authorized parties can decrypt

---

## 12. Implementation Requirements

### 12.1 Mandatory Features

All ledger implementations MUST:

- Support all event types defined in Section 2.2
- Implement hash-linking per Section 3
- Verify signatures per Section 4
- Provide REST API per Section 8.1
- Support event streaming (WebSocket or SSE)

### 12.2 Optional Features

Implementations MAY:

- Use Merkle batching (Section 5)
- Implement partitioning (Section 9)
- Provide GraphQL API
- Support subscriptions with filters

---

## 13. Compliance & Audit

### 13.1 Deterministic Replay

Any compliant implementation MUST be able to replay events from genesis and arrive at the same final state.

**Test**:

```bash
ledger-cli replay --from-genesis --to-sequence=10000 --verify-state
```

### 13.2 Audit API

```
GET /ledger/audit/verify-chain?start=0&end=10000
Response: { "valid": true, "breaks": [] }
```

---

## 14. Future Extensions

### 14.1 Zero-Knowledge Proofs

For private data: Events may include ZK proofs instead of plaintext inputs:

```typescript
interface PrivateEvent extends LedgerEvent {
  inputs: {
    commitment: string;  // Hash of private data
    zk_proof: string;    // Proof that computation is correct
  }
}
```

### 14.2 Cross-Chain Anchoring

For maximum decentralization, batch Merkle roots can be anchored to:

- Ethereum mainnet
- Bitcoin (via OP_RETURN)
- Celestia data availability layer

---

## 15. Examples

### 15.1 ContentCreated Event

```json
{
  "event_id": "evt_content_001",
  "event_type": "ContentCreated",
  "timestamp": 1702483200000,
  "sequence_number": 42,
  "actor": "did:key:zQ3shP2mWsZYWgvgM9kN3fM7V9Z1pZ",
  "modules": ["QFS", "SafetyGuard", "EconomicsGuard"],
  "inputs": {
    "content_cid": "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
    "text_hash": "0xabc123...",
    "media_cids": ["bafybei..."]
  },
  "outcome": {
    "status": "accepted",
    "coherence_score": 0.87,
    "reward_eligible": true
  },
  "policy_version": "v1.0.0",
  "guards_evaluated": [
    { "name": "SafetyGuard", "result": "pass", "score": 0.95 },
    { "name": "EconomicsGuard", "result": "pass", "score": 0.92 }
  ],
  "explanation": "Content passed all guards, coherence score 0.87",
  "previous_event_hash": "0xdef456...",
  "event_hash": "0x789abc...",
  "signature": "0xsig...",
  "signer_did": "did:key:node1"
}
```

### 15.2 RewardAllocated Event

```json
{
  "event_id": "evt_reward_001",
  "event_type": "RewardAllocated",
  "timestamp": 1702483300000,
  "sequence_number": 43,
  "actor": "did:key:system",
  "modules": ["TreasuryEngine"],
  "inputs": {
    "content_event_id": "evt_content_001",
    "reward_type": "coherence",
    "calculation_proof_cid": "bafybei..."
  },
  "outcome": {
    "recipient": "did:key:zQ3shP2mWsZYWgvgM9kN3fM7V9Z1pZ",
    "amount": 10.5,
    "token": "FLX",
    "vesting_schedule": null
  },
  "policy_version": "v1.0.0",
  "explanation": "Reward for coherent content (score 0.87)",
  "previous_event_hash": "0x789abc...",
  "event_hash": "0x012def...",
  "signature": "0xsig2...",
  "signer_did": "did:key:treasury-node"
}
```

---

## 16. Governance & Evolution

This specification is governed by the ATLAS x QFS community. Changes follow:

1. **Proposal**: Submit RFC to governance forum
2. **Discussion**: 2-week comment period
3. **Vote**: Token-weighted or reputation-weighted vote
4. **Activation**: Approved changes added to next minor/major version

---

**End of Specification v1.0.0**

---

## Appendix A: Canonical JSON

```typescript
function canonicalJSON(obj: unknown): string {
  // 1. Sort all object keys alphabetically
  // 2. No whitespace
  // 3. Unicode escape sequences for non-ASCII
  // 4. Null is "null", not undefined
  
  return JSON.stringify(obj, Object.keys(obj).sort(), 0);
}
```

## Appendix B: Reference Implementation

See: `backend/ledger/writer.py` and `backend/ledger/verifier.py` for Python reference implementation.
