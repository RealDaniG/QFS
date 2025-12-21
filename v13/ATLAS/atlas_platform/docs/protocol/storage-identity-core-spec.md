# ATLAS x QFS: Storage & Identity Core Specification

**Version**: 1.0.0  
**Phase**: 1  
**Status**: Draft  
**Last Updated**: December 13, 2025

---

## 1. Overview

The Storage & Identity Core defines the protocol-level types and operations for content storage (IPFS) and decentralized identity (DIDs) in ATLAS. This specification ensures clean integration with QFS and the Event Ledger in future phases.

### Design Principles

1. **Content-Addressed Everything**: All content identified by CID, not database IDs
2. **DID-Based Identity**: Users identified by DIDs, not email/username
3. **Ledger-Ready**: All operations produce structured data ready for ledger events
4. **Type Safety**: Explicit types for all protocol-facing objects
5. **Multi-Node**: No single IPFS node dependency

---

## 2. Core Types

### 2.1 Profile

User profile stored on IPFS, referenced by ledger.

```typescript
interface Profile {
  // Identity
  did: string;                    // User's DID (e.g., "did:key:z6Mkh...")
  
  // Profile content
  displayName: string;            // Human-readable name
  avatarCID?: string;             // IPFS CID of avatar image
  bioCID?: string;                // IPFS CID of bio text/markdown
  bannerCID?: string;             // IPFS CID of banner image
  
  // Links
  links?: {
    website?: string;
    twitter?: string;
    github?: string;
    [key: string]: string | undefined;
  };
  
  // Metadata (Phase 1: wall-clock hints, Phase 2: ledger sequence authoritative)
  createdAtMs: number;            // Wall-clock hint (Date.now()), non-authoritative
  updatedAtMs: number;            // Wall-clock hint, non-authoritative
  version: number;                // Profile version (increments on update)
  
  // Phase 2: Will add ledgerSequence and logicalTimestamp for authoritative ordering
  
  // Privacy settings (stored, not enforced here)
  preferences?: {
    visibility: 'public' | 'followers' | 'private';
    indexable: boolean;
  };
}
```

**Storage**:

- Profile JSON uploaded to IPFS
- Ledger stores only: `{ did, profileCID, createdAt }`
- Clients fetch full profile from IPFS using CID

### 2.2 ContentObject

Content item (post, media, etc.) stored on IPFS.

```typescript
type Visibility = 'public' | 'followers' | 'private' | 'unlisted';

interface ContentObject {
  // Content
  contentCID: string;             // IPFS CID of the actual content
  contentType: string;            // MIME type (e.g., "text/plain", "image/jpeg")
  
  // Authorship
  authorDID: string;              // Creator's DID
  
  // Metadata
  metadataCID?: string;           // Optional: CID of additional metadata JSON
  size: number;                   // Content size in bytes
  contentHash: string;            // SHA-256 of raw content bytes
  metadataHash?: string;          // SHA-256 of canonical JSON metadata
  
  // Context
  communityId?: string;           // Optional: community DID or identifier
  parentCID?: string;             // Optional: reply/quote reference
  tags?: string[];                // Content categorization
  
  // Timestamps (Phase 1: wall-clock hints, Phase 2: ledger sequence)
  createdAtMs: number;            // Wall-clock hint (Date.now()), non-authoritative
  
  // Privacy & Visibility
  visibility?: Visibility;        // Note: Only 'public'/'unlisted' eligible for QFS scoring
  encrypted?: boolean;            // If true, content is encrypted
  encryptionKeyRef?: string;      // Reference to encryption key (for E2E)
}
```

**Visibility Semantics**:

- `public`: Fully discoverable, eligible for QFS coherence scoring and rewards
- `unlisted`: Not in discovery feeds, but accessible via CID, eligible for QFS
- `followers`: Only visible to followers, NOT eligible for public QFS scoring
- `private`: Encrypted, only metadata hash in ledger, NOT eligible for QFS

### 2.3 SignedPayload

Generic structure for DID-signed data (reusable across profiles, content, events).

```typescript
interface SignedPayload<T> {
  payload: T;
  payloadHash: string;            // SHA-256 of canonical JSON of payload
  signerDID: string;
  signature: string;              // Ed25519 or PQC signature
}

// Helper functions (implemented in did/signer.ts)
function signWith DID<T>(did: string, payload: T): Promise<SignedPayload<T>>;
function verifySignedPayload<T>(signed: SignedPayload<T>): Promise<boolean>;
```

### 2.4 ContentEnvelope

Structured wrapper for content uploads, ready for ledger events.

```typescript
interface ContentEnvelope {
  // Core content (signed)
  signedContent: SignedPayload<ContentObject>;
  
  // Ledger preparation
  pendingEventType: 'ContentCreated' | 'ContentUpdated' | 'ContentDeleted';
  eventInputHash: string;         // SHA-256 of canonical JSON of full envelope
  
  // Pinning
  pinStatus: 'pending' | 'pinned' | 'failed';
  pinNodes?: string[];            // DIDs of nodes that pinned this content
}
```

### 2.5 PendingLedgerEvent

Abstract representation of events awaiting ledger write.

```typescript
interface PendingLedgerEvent<T = unknown> {
  // Event identification (TEMPORARY: Phase 1 only)
  eventType: string;              // e.g., "ContentCreated", "ProfileUpdated"
  pendingId: string;              // Local UUID for tracking (NOT in final ledger)
  
  // Actor
  actorDID: string;               // DID of event initiator
  
  // Event-specific data
  inputs: T;                      // Typed inputs (ContentCreated = ContentEnvelope)
  eventInputHash: string;         // SHA-256 of canonical JSON of inputs
  
  // Metadata (TEMPORARY: Phase 1 wall-clock hints)
  createdAtMs: number;            // When event was created locally (non-authoritative)
  status: 'pending' | 'submitted' | 'confirmed' | 'failed';
  
  // Eventual ledger reference (FINAL: Phase 2+)
  ledgerEventId?: string;         // Set when confirmed in ledger
  ledgerSequence?: number;        // Authoritative sequence number
}

// Specific event types
interface PendingContentCreatedEvent extends PendingLedgerEvent<ContentEnvelope> {
  eventType: 'ContentCreated';
}

interface PendingProfileUpdatedEvent extends PendingLedgerEvent<{ profileCID: string; profileHash: string }> {
  eventType: 'ProfileUpdated';
}
```

### 2.6 IPFSMetadata

IPFS-specific metadata for content management.

```typescript
interface IPFSMetadata {
  cid: string;
  size: number;
  pinned: boolean;
  pinnedBy?: string[];            // DIDs of nodes that pinned
  
  // Redundancy (actual vs desired)
  desiredRedundancy: number;      // From policy: how many nodes SHOULD pin
  currentRedundancy: number;      // Actual: how many nodes ARE pinning
  
  expiresAt?: number;             // Optional: TTL for ephemeral content
  
  // Encryption
  encrypted: boolean;
  encryptionMethod?: 'aes-256-gcm' | 'xchacha20-poly1305';
  
  // Chunking (for large files)
  chunked?: boolean;
  chunkSize?: number;
  totalChunks?: number;
}
```

---

## 2.7 Hashing Rules

**Canonical Hashing Function**: All hashes in ATLAS use SHA-256 with canonical JSON.

```typescript
function canonicalJSON(obj: unknown): string {
  // 1. Sort all object keys alphabetically (recursive)
  // 2. No whitespace
  // 3. UTF-8 encoding
  // 4. null is "null", undefined is omitted
  return JSON.stringify(obj, Object.keys(obj).sort(), 0);
}

function hashContent(bytes: Uint8Array): string {
  // SHA-256 of raw bytes
  return sha256(bytes);
}

function hashMetadata<T>(obj: T): string {
  // SHA-256 of canonical JSON
  const canonical = canonicalJSON(obj);
  return sha256(new TextEncoder().encode(canonical));
}
```

**Usage**:

- `contentHash` = `hashContent(rawContentBytes)`
- `metadataHash` = `hashMetadata(contentObject)`
- `eventInputHash` = `hashMetadata(pendingEvent.inputs)`
- `payloadHash` = `hashMetadata(signedPayload.payload)`

**Phase 2 Alignment**: Event Ledger will use identical canonicalization for `event_hash` and `previous_event_hash`.

---

## 3. IPFS Client Primitives

All IPFS operations MUST use these standardized primitives.

### 3.1 Upload Operations

```typescript
interface IPFSUploadResult {
  cid: string;
  size: number;
  mimeType?: string;
  hash: string;                   // SHA-256 of content
}

class IPFSClient {
  // Binary upload
  uploadContent(
    buffer: Buffer | Uint8Array | ReadableStream,
    options?: { filename?: string; mimeType?: string }
  ): Promise<IPFSUploadResult>;
  
  // JSON upload (convenience)
  uploadJson<T>(obj: T): Promise<IPFSUploadResult>;
  
  // Batch upload
  uploadBatch(
    files: Array<{ buffer: Buffer; filename: string }>
  ): Promise<IPFSUploadResult[]>;
}
```

### 3.2 Fetch Operations

```typescript
class IPFSClient {
  // Fetch as buffer
  fetch(cid: string): Promise<Uint8Array>;
  
  // Fetch as stream (for large files)
  fetchStream(cid: string): Promise<ReadableStream>;
  
  // JSON fetch (convenience)
  getJson<T>(cid: string): Promise<T>;
  
  // Verify content hash
  verifyContent(cid: string, expectedHash: string): Promise<boolean>;
}
```

### 3.3 Pinning Operations

```typescript
interface PinStatus {
  cid: string;
  pinned: boolean;
  pinnedAt?: number;
  pinnedBy?: string;              // Node DID
}

class IPFSClient {
  pin(cid: string, options?: { recursive?: boolean }): Promise<PinStatus>;
  unpin(cid: string): Promise<void>;
  isPinned(cid: string): Promise<boolean>;
  listPinned(filter?: { type?: 'all' | 'direct' | 'recursive' }): Promise<string[]>;
}
```

---

## 4. Separate Layers

### 4.1 DID Layer

**Purpose**: Identity and cryptographic operations

```typescript
// DID document (resolved from DID)
interface DIDDocument {
  id: string;                     // DID
  verificationMethod: Array<{
    id: string;
    type: string;
    controller: string;
    publicKeyMultibase: string;
  }>;
  authentication: string[];
  service?: Array<{
    id: string;
    type: string;
    serviceEndpoint: string;
  }>;
}
```

**Operations**:

- Resolve DID → DID Document
- Sign data with DID
- Verify signatures

### 4.2 Profile Layer

**Purpose**: User-facing profile information

**Storage**: IPFS (Profile JSON)  
**Reference**: Ledger event `ProfileCreated` / `ProfileUpdated`

**Operations**:

```typescript
function publishProfile(profile: Profile): Promise<{
  cid: string;
  hash: string;                   // Ready for ledger event
  pendingEvent: PendingProfileUpdatedEvent;
}>;

function loadProfile(cid: string): Promise<Profile>;
```

### 4.3 Ledger Layer (Placeholder for Phase 2)

**Purpose**: Immutable event log

**Operations** (to be implemented):

```typescript
function writeEvent(event: PendingLedgerEvent): Promise<{
  eventId: string;
  sequence: number;
}>;

function queryEvents(filter: EventFilter): Promise<LedgerEvent[]>;
```

**Current Phase 1 Behavior**:

- Store `PendingLedgerEvent` objects locally
- When Phase 2 arrives, batch-submit all pending events

---

## 5

 Content Upload Flow

### 5.1 Draft vs Publish Separation

**Phase 1 Behavior**: Support local drafts before IPFS upload.

```typescript
interface DraftContent {
  tempId: string;                 // Local UUID
  raw: Buffer | string;           // Raw content (not yet on IPFS)
  metadata: {
    type: string;
    communityId?: string;
    tags?: string[];
    visibility?: Visibility;
  };
  createdAtMs: number;            // Local creation time
}
```

**Two-Stage Publishing**:

1. **Create Draft** (local only, no IPFS):

```typescript
function createDraft(content: string | Buffer, metadata: DraftMetadata): DraftContent {
  return {
    tempId: crypto.randomUUID(),
    raw: content,
    metadata,
    createdAtMs: Date.now(),
  };
}
```

2. **Publish Draft** (IPFS upload + envelope + pending event):

```typescript
function publishDraft(draft: DraftContent, authorDID: string): Promise<ContentEnvelope>;
```

Drafts MAY be stored locally (IndexedDB) without IPFS. `publishDraft` is the finalization path that always produces a `ContentEnvelope` and `PendingLedgerEvent`.

### 5.2 Standard Publishing Flow

```
User creates content →
  1. Upload content to IPFS → contentCID
  2. Create ContentObject with metadata
  3. Wrap in ContentEnvelope
  4. Create PendingContentCreatedEvent
  5. Store locally until ledger write
  6. (Phase 2) Submit to ledger
  7. QFS picks up event, computes coherence
```

### 5.2 Implementation

```typescript
async function publishContent(
  content: Buffer | string,
  metadata: {
    type: string;
    communityId?: string;
    tags?: string[];
  },
  authorDID: string
): Promise<ContentEnvelope> {
  // 1. Upload to IPFS
  const uploadResult = await ipfsClient.uploadContent(content, {
    mimeType: metadata.type
  });
  
  // 2. Create ContentObject
  const contentObj: ContentObject = {
    contentCID: uploadResult.cid,
    contentType: metadata.type,
    authorDID,
    size: uploadResult.size,
    contentHash: uploadResult.hash,            // SHA-256 of bytes
    communityId: metadata.communityId,
    tags: metadata.tags,
    visibility: metadata.visibility || 'public',
    createdAtMs: Date.now(),                   // Wall-clock hint
  };
  
  // 3. Upload metadata
  const metadataResult = await ipfsClient.uploadJson(contentObj);
  contentObj.metadataCID = metadataResult.cid;
  contentObj.metadataHash = metadataResult.hash;  // SHA-256 of canonical JSON
  
  // 4. Sign content
  const signedContent = await signWithDID(authorDID, contentObj);
  
  // 5. Create envelope
  const envelope: ContentEnvelope = {
    signedContent,
    pendingEventType: 'ContentCreated',
    eventInputHash: hashMetadata(signedContent),
    pinStatus: 'pending',
  };
  
  // 6. Create pending ledger event
  const pendingEvent: PendingContentCreatedEvent = {
    eventType: 'ContentCreated',
    pendingId: crypto.randomUUID(),
    actorDID: authorDID,
    inputs: envelope,
    eventInputHash: hashMetadata(envelope),
    createdAtMs: Date.now(),
    status: 'pending',
  };
  
  // 7. Store locally (IndexedDB or similar)
  await storePendingEvent(pendingEvent);
  
  return envelope;
}
```

---

## 6. Multi-Node IPFS

### 6.1 Node Registry

```typescript
interface IPFSNodeInfo {
  did: string;                    // Node operator DID
  endpoint: string;               // API URL
  gateway: string;                // Gateway URL
  uptime: number;                 // Percentage
  latency: number;                // Avg latency (ms)
  pinnedCIDs: number;             // Count of pinned content
}

function getIPFSNodes(): Promise<IPFSNodeInfo[]>;
function selectNode(nodes: IPFSNodeInfo[]): IPFSNodeInfo;
```

### 6.2 Multi-Node Operations

**Node Selection Strategy** (default, clients MAY override):

```typescript
function scoreNode(node: IPFSNodeInfo): number {
  // Weighted scoring: uptime (40%), inverse latency (30%), pins (20%), reputation (10%)
  const uptimeScore = node.uptime;                          // 0-100
  const latencyScore = Math.max(0, 100 - node.latency);    // inverse latency
  const pinsScore = Math.min(100, node.pinnedCIDs / 100);  // normalized
  const reputationScore = 100;                              // TODO: From ledger/governance
  
  return (
    uptimeScore * 0.4 +
    latencyScore * 0.3 +
    pinsScore * 0.2 +
    reputationScore * 0.1
  );
}

function selectNode(nodes: IPFSNodeInfo[]): IPFSNodeInfo {
  return nodes.sort((a, b) => scoreNode(b) - scoreNode(a))[0];
}
```

**Error Handling Requirements**:

```typescript
class MultiNodeIPFSClient extends IPFSClient {
  async uploadContent(buffer: Buffer): Promise<IPFSUploadResult> {
    const attempts: Array<{ node: string; error: Error }> = [];
    
    for (const node of this.nodes) {
      try {
        return await this.uploadToNode(node, buffer);
      } catch (error) {
        attempts.push({ node: node.did, error: error as Error });
      }
    }
    
    // All nodes failed - MUST throw with diagnostics
    throw new IPFSError(
      'All IPFS nodes failed',
      'UPLOAD_ALL_NODES_FAILED',
      new AggregateError(
        attempts.map(a => a.error),
        `Tried ${attempts.length} nodes: ${attempts.map(a => a.node).join(', ')}`
      )
    );
  }
  
  async fetch(cid: string): Promise<Uint8Array> {
    // Use Promise.any for "first success" behavior
    const promises = this.nodes.map(async (node) => {
      const data = await this.fetch FromNode(node, cid);
      // Log which node served the content (for reputation/weighting)
      console.log(`CID ${cid} served by node ${node.did}`);
      return data;
    });
    
    try {
      return await Promise.any(promises);
    } catch (error) {
      throw new IPFSError(
        `Failed to fetch CID ${cid} from any node`,
        'FETCH_ALL_NODES_FAILED',
        error as Error
      );
    }
  }
}
```

---

## 7. Pinning Incentives (Preparation)

### 7.1 Critical CIDs Registry

```typescript
interface PinningTarget {
  cid: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  reason: string;
  rewardRate?: number;            // FLX/day for pinning
  minRedundancy: number;          // Required number of nodes
}

// API endpoint for node operators
GET /api/pinning/targets
Response: {
  targets: PinningTarget[]
}
```

### 7.2 Integration

In content upload flow, mark important content:

```typescript
if (metadata.communityId === 'governance' || metadata.tags?.includes('policy')) {
  await markForIncentivizedPinning(uploadResult.cid, {
    priority: 'high',
    minRedundancy: 5,
    policyVersion: 'v1.0.0'        // QFS policy that defines the reward
  });
}
```

**Pinning Target with Policy Alignment**:

```typescript
interface PinningTarget {
  cid: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  reason: string;
  rewardRate?: number;            // FLX/day (ADVISORY only)
  minRedundancy: number;
  policyVersion?: string;         // QFS PolicyRegistry version defining rewards
}
```

**Important**: Actual rewards determined by QFS `NodeRewardAllocated` ledger events. This API is advisory for convenience and MUST NOT be treated as authoritative.

---

## 8. Phase 1 Acceptance Criteria

### 8.1 IPFS Client

- [ ] Supports `uploadContent`, `fetch`, `pin` for binary and JSON
- [ ] Has retry logic with exponential backoff
- [ ] Clear error types (`IPFSClientError` with codes)
- [ ] Multi-node support with automatic failover
- [ ] Gateway URL generation for content display

### 8.2 DID + Profiles

- [ ] DIDs generated and stored securely (encrypted in browser storage)
- [ ] Profile documents versioned (each update = new CID)
- [ ] Clear mapping: DID → profileCID → resolved Profile
- [ ] Profile operations use `publishProfile` / `loadProfile` primitives

### 8.3 Content Upload

- [ ] Every published post has `contentCID` and round-trips correctly
- [ ] `ContentEnvelope` wrapper used for all content
- [ ] `PendingContentCreatedEvent` created and stored locally
- [ ] Content hash verifiable against CID

### 8.4 Ledger Preparation

- [ ] All operations produce structured `PendingLedgerEvent` objects
- [ ] Pending events stored in IndexedDB with status tracking
- [ ] Migration path documented for Phase 2 ledger integration

---

## 9. Migration to Phase 2

### 9.1 Final vs Temporary Fields

**FINAL Fields** (won't change in Phase 2):

- `Profile`, `ContentObject`, `ContentEnvelope`, `SignedPayload` shapes
- `PendingLedgerEvent` structure (only adding `ledgerEventId`, `ledgerSequence`)
- IPFS primitives (upload/fetch/pin)
- Hashing rules (SHA-256, canonical JSON)
- DID signatures

**TEMPORARY Fields** (Phase 1 only, replaced in Phase 2):

- `pendingId` → Local UUID, NOT in final ledger
- `createdAtMs`, `updatedAtMs` → Wall-clock hints, replaced by `ledgerSequence` for ordering
- Local IndexedDB storage → Replaced by ledger writes
- `status: 'pending'` → All events will be `'confirmed'` in ledger

### 9.2 Migration Mechanics

When Event Ledger goes live:

```typescript
// Phase 1: Store locally
await storePendingEvent(pendingEvent);

// Phase 2: Replace local storage with ledger writes
const ledgerEvent = await ledgerClient.writeEvent({
  event_type: pendingEvent.eventType,
  actor: pendingEvent.actorDID,
  inputs: pendingEvent.inputs,           // Same structure!
  modules: ['IPFS', 'QFS'],
  // Ledger adds:
  sequence_number: 12345,                 // Authoritative ordering
  timestamp: logicalClock.now(),          // Logical timestamp
  previous_event_hash: previousHash,
  // ... etc per ledger-spec.md
});

// Update pending event
pendingEvent.status = 'confirmed';
pendingEvent.ledgerEventId = ledgerEvent.event_id;
pendingEvent.ledgerSequence = ledgerEvent.sequence_number;
```

**Batch Migration**: All stored `PendingLedgerEvent` objects can be batch-submitted to ledger with single script.

### 9.3 Ordering Semantics

**Phase 1**: Clients use `createdAtMs` for display ordering (UX hint only)

**Phase 2**: Authoritative ordering comes from `ledgerSequence`:

```typescript
// Phase 1
events.sort((a, b) => a.createdAtMs - b.createdAtMs);  // Local hint

// Phase 2
events.sort((a, b) => a.ledgerSequence! - b.ledgerSequence!);  // Authoritative
```

### 9.4 Compatibility Promise

All Phase 1 types are designed to be **forward-compatible**:

- Adding fields (e.g., `ledgerSequence`) is non-breaking
- Removing fields (e.g., `pendingId`) only affects local code, not protocol
- Hash algorithms remain identical
- SignedPayload structure works for both local and ledger events

**Zero refactoring required** for core types when ledger goes live.

---

## 10. Example: Full Content Creation

```typescript
// 1. User creates post
const postText = "Hello ATLAS!";

// 2. Upload to IPFS
const envelope = await publishContent(
  Buffer.from(postText),
  { type: 'text/plain', tags: ['introduction'] },
  userDID
);

// 3. Display immediately (UX)
displayPost({
  cid: envelope.content.contentCID,
  author: envelope.content.authorDID,
  text: postText,
  pending: true  // Not yet in ledger
});

// 4. Later (Phase 2): Ledger confirms event
// Update UI to show confirmed status
```

---

**End of Storage & Identity Core Specification v1.0.0**
