# QFS × ATLAS User Data Model & Storage Strategy

> **Version:** v18.9  
> **Date:** 2025-12-20  
> **Status:** Operational Specification

## Executive Summary

This document defines how QFS × ATLAS handles user data across three storage classes to maintain **deterministic, replayable, privacy-first** guarantees while supporting a functional social application.

**Core Principle:** Immutable ledger facts (Class A) are separated from mutable user-facing data (Class B) and ephemeral telemetry (Class C).

---

## 1. Storage Classes

### Class A: Ledger-Critical Events

**Storage:** EvidenceBus (immutable, replicated via Raft consensus)  
**Contents:** Governance decisions, bounty allocations, dispute resolutions, message anchors  
**Characteristics:**

- Fully deterministic and replayable
- Pseudonymous (wallet addresses, user_ids, hashes only)
- No direct PII (names, emails, free-text identifiers)
- Permanent retention for audit trail

**Event Examples:**

- `PROPOSAL_CREATED`: proposal_id, creator_wallet, content_hash, timestamp
- `VOTE_CAST`: proposal_id, voter_wallet, vote_value, timestamp
- `BOUNTY_CLAIMED`: bounty_id, claimant_wallet, amount, timestamp
- `MESSAGE_POSTED`: message_hash, sender_wallet, channel_id, timestamp

### Class B: Social/Personal Data

**Storage:** Projection/UX Databases (PostgreSQL, Redis, or application-layer stores)  
**Contents:** Chat message bodies, user profiles, display names, bios, avatars, preferences  
**Characteristics:**

- Mutable and redactable
- Supports deletion and anonymization (GDPR compliance)
- Anchored in Class A via content hashes when integrity is required
- User-controlled retention

**Data Examples:**

- User profiles: display_name, bio, avatar_url, contact_preferences
- Chat messages: full message content, formatting, attachments
- Space metadata: descriptions, member lists, channel settings
- User preferences: theme, notification settings, language

### Class C: Ephemeral/Telemetry

**Storage:** Short-lived caches, log aggregation systems  
**Contents:** Metrics, performance data, advisory outputs, Ascon AEAD operation logs  
**Characteristics:**

- Time-limited retention (7-30 days)
- Anonymized aggregation for analytics
- No long-term storage of individual user actions
- Minimal PII exposure

**Data Examples:**

- Session metrics: login counts, active session duration
- API performance: request latency, error rates
- Advisory outputs: content analysis results (anonymized)
- Ascon operations: encryption/decryption events with context only

---

## 2. Event Classification Matrix

| Event Type | Class | EvidenceBus Fields | Projection Fields | Notes |
|------------|-------|-------------------|-------------------|-------|
| **Governance** |
| PROPOSAL_CREATED | A | proposal_id, creator_wallet, content_hash, timestamp | title, description, full_content | Content hash anchors mutable description |
| VOTE_CAST | A | proposal_id, voter_wallet, vote_value, timestamp | - | Fully immutable |
| PROPOSAL_FINALIZED | A | proposal_id, outcome, vote_tally_hash, timestamp | detailed_results | Tally hash anchors full results |
| **Bounties** |
| BOUNTY_CREATED | A | bounty_id, creator_wallet, amount, criteria_hash | title, description, deliverables | Criteria hash anchors requirements |
| BOUNTY_CLAIMED | A | bounty_id, claimant_wallet, timestamp | - | Fully immutable |
| BOUNTY_PAID | A | bounty_id, recipient_wallet, amount, timestamp | - | Fully immutable |
| **Social/Chat** |
| MESSAGE_POSTED | A | message_hash, sender_wallet, channel_id, timestamp | message_content, formatting, attachments | Hash anchors mutable content |
| SPACE_CREATED | A | space_id, creator_wallet, timestamp | space_name, description, settings | Minimal anchor in ledger |
| USER_JOINED_SPACE | A | space_id, user_wallet, timestamp | - | Membership fact is immutable |
| **Auth** |
| AUTH_LOGIN | C | session_id, wallet (hashed), node_id, timestamp | - | Telemetry only |
| AUTH_LOGOUT | C | session_id, timestamp | - | Telemetry only |
| **User Profiles** |
| PROFILE_CREATED | - | - | user_id, wallet, display_name, bio, avatar | Fully Class B |
| PROFILE_UPDATED | B | profile_hash (optional) | updated_fields | Optional hash for integrity |

---

## 3. Pseudonymization & User Identity

### User ID Strategy

**Primary Identifier:** `user_id` (deterministic hash of wallet address)

```python
user_id = hashlib.sha256(f"user:{wallet_address}".encode()).hexdigest()[:16]
```

**Mapping:**

- EvidenceBus events reference `user_id` or `wallet_address` only
- Class B projection stores mapping: `user_id` → profile data
- No email addresses or real names in Class A events

### Display Names and Profiles

**Class B Storage:**

```json
{
  "user_id": "a3f2c1d4e5b6a7f8",
  "wallet_address": "0xABC123...",
  "display_name": "Alice",
  "bio": "Blockchain enthusiast",
  "avatar_url": "ipfs://Qm...",
  "created_at": 1703001234.5,
  "updated_at": 1703002345.6
}
```

**EvidenceBus References:**

- Governance: `creator_wallet: "0xABC123..."`
- Chat: `sender_wallet: "0xABC123..."`
- Optional: `sender_display_name_hash` for UI consistency checks

---

## 4. Content Hashing & Anchoring

### Message Anchoring

**Purpose:** Ensure message integrity while keeping content mutable for moderation

**Process:**

1. User posts message → full content stored in Class B
2. Compute message hash: `sha256(message_content + metadata)`
3. Emit `MESSAGE_POSTED` event to EvidenceBus with hash only
4. UI displays content from Class B, verifies hash against anchor

**Example:**

```python
# Class B (projection)
message = {
    "message_id": "msg_12345",
    "sender_wallet": "0xABC123...",
    "channel_id": "governance_123",
    "content": "I support this proposal because...",
    "timestamp": 1703001234.5
}

# Class A (EvidenceBus)
event = {
    "type": "MESSAGE_POSTED",
    "message_hash": sha256(message_content),
    "sender_wallet": "0xABC123...",
    "channel_id": "governance_123",
    "timestamp": 1703001234.5
}
```

### Proposal Content Anchoring

**Governance Proposals:**

- Title and description stored in Class B
- Content hash stored in Class A
- Changes to description create new hash → new event

---

## 5. Privacy & Deletion Flows

### User Data Rights

**"Forget Me" Request:**

1. User initiates deletion via ATLAS UI
2. Class B projection deletes/anonymizes:
   - Profile data → replaced with tombstone: `{user_id: "deleted_user", display_name: "[Deleted]"}`
   - Chat messages → content replaced with `"[Message deleted by user]"`
   - Preferences and settings → purged
3. Class A events remain intact:
   - `VOTE_CAST` events still show wallet address (required for governance integrity)
   - Message hashes remain for ordering verification
4. Emit audit event: `USER_DATA_ANONYMIZED`

**Moderation Actions:**

- Remove harmful content from Class B projections
- Retain anchor hash in Class A for audit trail
- Mark as `[Removed by moderator]` in UI

### Crypto-Shredding (Future)

For Ascon-protected advisory payloads:

- Delete encryption keys after retention period
- Ciphertext becomes unreadable without re-keying
- PoE anchor remains verifiable

---

## 6. Session Tokens & Auth Data

### Ascon Session Tokens (Class C)

**Token Payload:**

```json
{
  "wallet_address": "0xABC123...",
  "scopes": ["bounty:read", "governance:vote"],
  "created_at": 1703001234.5,
  "expires_at": 1703087634.5
}
```

**Characteristics:**

- Stateless (no server-side storage)
- Ascon AEAD encrypted with deterministic nonce
- Minimal claims (no PII beyond wallet)
- PoE logged: `AUTH_LOGIN`, `AUTH_LOGOUT` with hashed session_id only

**Revocation List:**

- `session_id` → `revoked_at` timestamp
- Temporary storage (2x TTL retention)
- No sensitive content

---

## 7. Observability & Compliance

### Data Volume Metrics

**Track per storage class:**

- Class A: Events/day, storage growth, PII exposure checks
- Class B: Records, update frequency, deletion requests
- Class C: Cache size, retention adherence, anonymization coverage

**Dashboard Indicators:**

- ⚠️ Warning: Event schema contains unexpected PII fields
- ✅ Healthy: All Class A events use pseudonymous identifiers
- 📊 Metric: Class B deletion requests processed / pending

### Audit Events

**Class B Operations:**

- `PROFILE_ANONYMIZED`: user_id, timestamp, admin_wallet (if applicable)
- `CHAT_HISTORY_PURGED`: user_id, message_count, timestamp
- `CONTENT_MODERATED`: content_hash, action, moderator_wallet, timestamp

**PoE Integration:**

- Audit events emit hash anchors to EvidenceBus for non-repudiation
- Full details stored in Class B projection logs

---

## 8. Implementation Checklist

### Phase 1: Documentation & Schema (Complete)

- [x] Define storage classes and classification matrix
- [x] Document pseudonymization strategy
- [x] Establish deletion and privacy flows

### Phase 2: Projection Layer (In Progress)

- [ ] Implement Class B database schema for profiles, messages, spaces
- [ ] Create projection services that consume EvidenceBus events
- [ ] Wire ATLAS API to read/write Class B data through adapters

### Phase 3: Anchoring & Integrity

- [ ] Implement content hashing for messages and proposals
- [ ] Emit `MESSAGE_POSTED` with hash-only to EvidenceBus
- [ ] Add verification layer in UI (hash validation)

### Phase 4: Privacy Operations

- [ ] Implement "forget me" deletion flow
- [ ] Create moderation tools with Class B content removal
- [ ] Test anonymization → verify ledger integrity preserved

### Phase 5: Compliance & Testing

- [ ] Add schema validation CI checks (no PII in Class A)
- [ ] End-to-end privacy flow tests
- [ ] Observability dashboard for data classification

---

## 9. Migration Path for Existing Data

### Current State Analysis

**ATLAS v17/v18 Status:**

- Governance events: Already Class A compliant (no PII)
- Bounty events: Already Class A compliant
- Chat: Currently mocked → needs Class B projection
- Profiles: Currently in-memory → needs Class B projection

### Migration Steps

1. **Audit existing EvidenceBus events:**
   - Scan for unexpected PII fields
   - Document any violations and create remediation plan

2. **Backfill projections:**
   - Replay EvidenceBus events to populate Class B databases
   - Ensure deterministic replay yields consistent projections

3. **Deprecate legacy schemas:**
   - Mark old event versions with PII as deprecated
   - Migrate to pseudonymized versions with grace period

---

## 10. References

- [ATLAS v18 Gap Report](./ATLAS_V18_GAP_REPORT.md)
- [Auth Sync Migration](./AUTH_SYNC_V18_MIGRATION.md)
- [Platform Evolution Plan](./PLATFORM_EVOLUTION_PLAN.md)
- [Zero-Sim Compliance](../scripts/check_zero_sim.py)
- [Ascon Adapter](../v18/crypto/ascon_adapter.py)

---

**Maintained by:** QFS × ATLAS Core Team  
**Last Updated:** 2025-12-20  
**Next Review:** v18.10 (Projection Layer Complete)
