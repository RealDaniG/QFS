/**
 * Protocol-Level Types for ATLAS Storage & Identity v2
 * As defined in docs/protocol/storage-identity-core-spec.md
 * Updated with all Phase 1 refinements
 */

// ============================================================================
// Core Visibility Types
// ============================================================================

export type Visibility = 'public' | 'followers' | 'private' | 'unlisted';

// ============================================================================
// Profile Types
// ============================================================================

export interface Profile {
    // Identity
    did: string;

    // Profile content
    displayName: string;
    avatarCID?: string;
    bioCID?: string;
    bannerCID?: string;

    // Links
    links?: {
        website?: string;
        twitter?: string;
        github?: string;
        [key: string]: string | undefined;
    };

    // Metadata (Phase 1: wall-clock hints)
    createdAtMs: number;        // Wall-clock hint, non-authoritative
    updatedAtMs: number;
    version: number;

    // Privacy settings
    preferences?: {
        visibility: Visibility;
        indexable: boolean;
    };
}

// ============================================================================
// Content Types
// ============================================================================

export interface ContentObject {
    // Content
    contentCID: string;
    contentType: string;          // MIME type

    // Authorship
    authorDID: string;

    // Metadata
    metadataCID?: string;
    size: number;
    contentHash: string;          // SHA-256 of raw bytes
    metadataHash?: string;        // SHA-256 of canonical JSON

    // Context
    communityId?: string;         // Community DID or identifier
    parentCID?: string;
    tags?: string[];

    // Timestamps (Phase 1: wall-clock hints)
    createdAtMs: number;

    // Privacy & Visibility
    visibility?: Visibility;
    encrypted?: boolean;
    encryptionKeyRef?: string;
}

// ============================================================================
// Signed Payload (Generic signing structure)
// ============================================================================

export interface SignedPayload<T> {
    payload: T;
    payloadHash: string;          // SHA-256 of canonical JSON
    signerDID: string;
    signature: string;
}

export interface ContentEnvelope {
    // Core content (signed)
    signedContent: SignedPayload<ContentObject>;

    // Ledger preparation
    pendingEventType: 'ContentCreated' | 'ContentUpdated' | 'ContentDeleted';
    eventInputHash: string;       // SHA-256 of canonical JSON of envelope

    // Pinning
    pinStatus: 'pending' | 'pinned' | 'failed';
    pinNodes?: string[];
}

// ============================================================================
// Draft Content (Phase 1 pre-publish)
// ============================================================================

export interface DraftContent {
    tempId: string;
    raw: Buffer | string;
    metadata: {
        type: string;
        communityId?: string;
        tags?: string[];
        visibility?: Visibility;
    };
    createdAtMs: number;
}

// ============================================================================
// Pending Ledger Event Types
// ============================================================================

export interface PendingLedgerEvent<T = unknown> {
    // Event identification (TEMPORARY: Phase 1 only)
    eventType: string;
    pendingId: string;            // Local UUID, NOT in final ledger

    // Actor
    actorDID: string;

    // Event-specific data
    inputs: T;
    eventInputHash: string;       // SHA-256 of canonical JSON

    // Metadata (TEMPORARY: Phase 1 wall-clock hints)
    createdAtMs: number;
    status: 'pending' | 'submitted' | 'confirmed' | 'failed';

    // Eventual ledger reference (FINAL: Phase 2+)
    ledgerEventId?: string;
    ledgerSequence?: number;
}

export interface PendingContentCreatedEvent extends PendingLedgerEvent<ContentEnvelope> {
    eventType: 'ContentCreated';
}

export interface PendingProfileUpdatedEvent extends PendingLedgerEvent<{
    profileCID: string;
    profileHash: string;
}> {
    eventType: 'ProfileUpdated';
}

export interface PendingInteractionEvent extends PendingLedgerEvent<{
    interactionType: 'like' | 'comment' | 'repost' | 'quote';
    targetCID: string;
    contentCID?: string;
}> {
    eventType: 'InteractionCreated';
}

// ============================================================================
// IPFS Types
// ============================================================================

export interface IPFSUploadResult {
    cid: string;
    size: number;
    mimeType?: string;
    hash: string;                 // SHA-256 of content
}

export interface IPFSMetadata {
    cid: string;
    size: number;
    pinned: boolean;
    pinnedBy?: string[];

    // Redundancy (actual vs desired)
    desiredRedundancy: number;
    currentRedundancy: number;

    expiresAt?: number;

    // Encryption
    encrypted: boolean;
    encryptionMethod?: 'aes-256-gcm' | 'xchacha20-poly1305';

    // Chunking
    chunked?: boolean;
    chunkSize?: number;
    totalChunks?: number;
}

export interface PinStatus {
    cid: string;
    pinned: boolean;
    pinnedAt?: number;
    pinnedBy?: string;
}

export interface IPFSNodeInfo {
    did: string;
    endpoint: string;
    gateway: string;
    uptime: number;
    latency: number;
    pinnedCIDs: number;
}

// ============================================================================
// Pinning Incentives
// ============================================================================

export type PinningPriority = 'critical' | 'high' | 'medium' | 'low';

export interface PinningTarget {
    cid: string;
    priority: PinningPriority;
    reason: string;
    rewardRate?: number;          // FLX/day (ADVISORY only)
    minRedundancy: number;
    policyVersion?: string;       // QFS PolicyRegistry version
}

// ============================================================================
// DID Types
// ============================================================================

export interface DIDDocument {
    id: string;
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

// ============================================================================
// Error Types
// ============================================================================

export class StorageError extends Error {
    constructor(
        message: string,
        public code: string,
        public cause?: Error
    ) {
        super(message);
        this.name = 'StorageError';
    }
}

export class IPFSError extends StorageError {
    constructor(message: string, code: string, cause?: Error) {
        super(message, code, cause);
        this.name = 'IPFSError';
    }
}

export class DIDError extends StorageError {
    constructor(message: string, code: string, cause?: Error) {
        super(message, code, cause);
        this.name = 'DIDError';
    }
}

// ============================================================================
// Hashing & Utilities
// ============================================================================

export interface HashAlgorithm {
    name: 'SHA-256';
    digest(data: Uint8Array | string): Promise<string>;
}

/**
 * Canonical JSON stringify for deterministic hashing
 * Sort keys, no whitespace, UTF-8
 */
export function canonicalJSON(obj: unknown): string {
    if (typeof obj !== 'object' || obj === null) {
        return JSON.stringify(obj);
    }

    if (Array.isArray(obj)) {
        return `[${obj.map(canonicalJSON).join(',')}]`;
    }

    const sorted = Object.keys(obj as object)
        .sort()
        .filter(key => (obj as Record<string, unknown>)[key] !== undefined);

    const pairs = sorted.map(
        key => `"${key}":${canonicalJSON((obj as Record<string, unknown>)[key])}`
    );

    return `{${pairs.join(',')}}`;
}

/**
 * SHA-256 hash of raw bytes
 */
export async function hashContent(bytes: Uint8Array): Promise<string> {
    const hashBuffer = await crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(hashBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

/**
 * SHA-256 hash of canonical JSON
 */
export async function hashMetadata<T>(obj: T): Promise<string> {
    const canonical = canonicalJSON(obj);
    return hashContent(new TextEncoder().encode(canonical));
}

// ============================================================================
// Event Filter
// ============================================================================

export interface EventFilter {
    eventType?: string;
    actorDID?: string;
    startSequence?: number;
    endSequence?: number;
    limit?: number;
}
