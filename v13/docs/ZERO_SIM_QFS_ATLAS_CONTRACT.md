# Zero-Simulation QFS × ATLAS Contract (v1.4)

> **Authority:** This document supersedes all local slice-level configuration.  
> **Enforcement:** Verified by `run_zero_sim_suite.py` and strictly enforced by CI.  
> **Effective:** 2025-12-18  
> **Changes in v1.4:** Codifies ATLAS v14 social-layer determinism, economic wiring, canonical contracts, and unified social regression requirements.

***

## 1. The Prime Invariant: Economic Truth

**QFS is the sole source of economic truth.**

- **No ATLAS Mutation:** The ATLAS frontend, API, and database layers **must never** directly mutate balances, mint tokens, or issue rewards.
- **Read-Only Projections:** All values displayed in ATLAS (Wallet, Profile, Feed) must be derived from a **read-only replay** of QFS ledger events.
- **Intent-Only Writes:** ATLAS may only submit **signed intents** (DRV packets) to the QFS consensus layer (or AEGIS API).

***

## 2. Zero-Simulation Compliance (System-Wide)

Every component in the critical path (Logic → Economics → Explanation) must adhere to:

### 2.1 No Randomness

- **Forbidden:** `random.random()`, `uuid.uuid4()`, `os.urandom()`, `Math.random()`, `crypto.randomBytes()` in consensus/economics paths.
- **Allowed:**
  - Deterministic PRNG seeded by `SHA-3(content_hash || ledger_state)`.
  - PQC key generation (one-time, externally signed, logged to ledger).
  - **Client-side optimistic UUIDs** IF and ONLY IF replaced by ledger-assigned canonical IDs upon ingestion.
- **Example (ATLAS v14):** Uses deterministic `DeterministicID.from_string(seed)` to derive `space_id`, `post_id`, and `message_id`; no random UUIDs are allowed in these paths.

### 2.2 No Wall-Clock Time

- **Forbidden:** `time.time()`, `datetime.now()`, `new Date()`, `Date.now()` in consensus/economics/replay paths.
- **Allowed:**
  - `DRV_Packet.timestamp` (ledger time).
  - `block_height` or `epoch_counter`.
  - Event timestamps passed explicitly from ledger.
  - **Metadata-only timestamps** (e.g., server ingestion time) that are **never used for ordering, caps, or economics**.
- **Example (ATLAS v14):** Spaces/Wall/Chat tests and regression scripts pass timestamps explicitly; no use of `time.time()` inside economic or ordering logic.

### 2.3 No Floating Point Economics

- **Forbidden:** `float`, `double`, `Number` (JS) for any token/value/reward calculation.
- **Allowed:**
  - `BigNum128`, `Decimal` with fixed precision (e.g., 18 decimals for ATR).
  - Integer-scaled arithmetic (e.g., micro-ATR: `1 ATR = 10^6 units`).
  - Floating point **only** for display formatting, clearly marked.
- **Example (ATLAS v14):** All social rewards (FLX/CHR) are computed via `BigNum128` and `CertifiedMath`; floats are used only for display or documentation, never in ledger-facing code.

### 2.4 No External I/O in Consensus

- **Forbidden:** Network calls, filesystem reads/writes, database queries in economics/guard/replay logic.
- **Allowed:**
  - Pure functions.
  - In-memory structures.
  - Deterministic fixtures for tests.
  - **Read-only ledger client** with explicit dependency injection.

### 2.5 No Hidden State / Mutable Globals

- **Forbidden:** Mutable global caches, singletons with time-based expiry, thread-local storage that varies by environment.
- **Allowed:**
  - Immutable config loaded once at startup.
  - Deterministic registries (PolicyRegistry, SignalRegistry).
  - Explicit dependency injection.

***

## 3. AEGIS Integration (NEW - Critical)

**AEGIS is the identity and permissioning layer. All privileged operations MUST route through AEGIS.**

### 3.1 Identity Verification

- **DID-Based Auth:** All user actions requiring economic effects (post, vote, reward claim) must be signed with a verified DID.
- **AEGIS Verification API:**
  - `POST /aegis/verify` must be called for every privileged action.
  - Response includes: `{verified: bool, user_id, reputation_tier, permissions[]}`.
- **No Fallback:** If AEGIS is unreachable, the system must **fail closed** (reject action), never bypass.

### 3.2 Permission Boundaries

- **Creator Permissions:** Only AEGIS-verified creators can submit content that is eligible for rewards.
- **Governance Permissions:** Only AEGIS-verified governance participants can vote on policy changes.
- **Node Operator Permissions:** Only AEGIS-verified nodes can participate in storage/proof obligations.

### 3.3 Reputation Integration

- **ATR (Author Trust Rank):** Derived from AEGIS reputation score + ledger history.
- **Guard Integration:** Guards (safety, coherence, ethics) must query AEGIS for user reputation tier before applying caps/bonuses.
- **Transparency:** AEGIS verification results must be logged to QFS ledger as `AEGISVerificationEvent` with signature.

### 3.4 Sybil Resistance

- **Rate Limits:** AEGIS enforces per-DID rate limits (e.g., max 10 posts/hour, max 100 votes/epoch).
- **Economic Staking:** High-value actions (governance proposals, node registration) require staking ATR/FLX, verified by AEGIS.
- **Appeal Path:** Users can appeal AEGIS denials via a governed, encrypted appeal channel (see Secure Chat integration).

***

## 4. Cryptographic Verification (NEW - Critical)

All economic events and explanations must be cryptographically verifiable.

### 4.1 PQC Signatures

- **Required:** All ledger entries, policy updates, and AEGIS verifications must be signed with post-quantum cryptographic (PQC) signatures.
- **Algorithms:** CRYSTALS-Dilithium (signatures), CRYSTALS-Kyber (key exchange).
- **No Fallback:** If PQC libraries are unavailable, the system must **fail to start**, not silently use weaker crypto.

### 4.2 Merkle Proofs

- **Content Integrity:** All content stored in StorageEngine must have a Merkle proof linking it to the ledger root.
- **Replay Verification:** Explanation endpoints must include a Merkle proof that the events they replayed are part of the canonical ledger.

### 4.3 Explanation Hashes

- **SHA-3-256:** Every explanation object must include a SHA-3-256 hash computed over canonical JSON (sorted keys, no whitespace).
- **Tamper Detection:** Clients can recompute the hash to detect tampering.
- **Audit Trail:** Explanation hashes must be logged to QFS ledger as `ExplanationAuditEvent`.

***

## 5. Slice-Level Invariants

### 5.1 Humor / Signal Slices

- **Pure Signals:** SignalAddons must emit `SignalResult` only. They cannot trigger payouts directly.
- **Replayability:** A signal score must be reproducible given the same `(Content, Context, Policy)` tuple.
- **AEGIS Integration:** Signals may query AEGIS reputation tier to adjust weights (e.g., veteran creators get +10% humor weight).

### 5.2 Value Nodes

- **Derived State:** A Value Node's state is a pure function of `Σ(Events)`.
- **Reference Graph:** The `ValueGraphRef` must be constructible from the event log without external database queries.
- **AEGIS Linkage:** Each Value Node must link to an AEGIS-verified DID.

### 5.3 Storage Engine

- **Content Addressing:** All content is referenced by immutable hash (CID).
- **Proof Replay:** Storage proofs must be verifiable against the QFS ledger history.
- **AEGIS Node Verification:** Only AEGIS-verified nodes can participate in storage replication and proof generation.

### 5.4 ATLAS Social Layer (Spaces, Wall, Chat) – v14

- **Deterministic IDs Only**
  - Space IDs, Wall Post IDs, and Chat Message IDs must be derived from deterministic functions of input parameters (e.g., SHA-256/UUIDv5 over `space_id:wallet:timestamp:content_head`).
  - No `uuid4` or similar random IDs are permitted in ATLAS surfaces that participate in economics or ordering.

- **Economically Aware vs Neutral Actions**
  - All social actions that affect value (balances, rewards, costs) MUST emit a corresponding `EconomicEvent` (e.g., `space_created`, `space_joined`, `space_spoke`, `wall_post_created`, `wall_post_liked`, `chat_session_created`, `chat_message_sent`).
  - Neutral actions (0-cost, 0-reward) such as:
    - `space_role_changed`, `space_member_kicked`, `space_member_muted`, `wall_post_pinned` / `wall_post_unpinned`
    MUST be explicitly documented as neutral and MUST NOT modify balances or mint/burn tokens.

- **Cross-Surface Linking**
  - Recap posts (`is_recap=True`) MUST link to Spaces via `space_id` (or `linked_space_id`) using deterministic IDs only.
  - Chat messages MAY reference Spaces or Wall Posts via a `references` list of IDs; these references are structural only and MUST NOT introduce hidden economics or non-deterministic ordering.

- **Social Regression Requirement**
  - A unified social regression script (currently `phase_v14_social_full.py`) MUST:
    - Execute a full lifecycle scenario across Spaces, Wall, and Chat using a single log.
    - Produce a stable SHA-256 hash over the canonical log representation.
  - CI MUST fail if this hash changes without an approved contract update, as this constitutes a behavior change of the social layer.

- **Canonical Contracts**
  - ATLAS v14 defines canonical Pydantic contracts (`AtlasSpace`, `AtlasWallPost`, `AtlasChatSession`, `AtlasChatMessage` in `v13/atlas/contracts.py`) as the **only** supported external schema for social data.
  - Internal structures (e.g., internal participant maps, muted/banned sets) MUST NOT be relied upon by external clients and MAY change without contract version bumps.
  - All explanation and replay tooling MUST project to these canonical contracts when presenting social state.

***

## 6. Explanation & Transparency

**"If you can't explain it via replay, you can't show it."**

- **Explanation Hash:** Every `/explain/*` response must include a SHA-3-256 hash of the explanation object.
- **Policy Versioning:** Explanations must cite the specific Policy ID/Hash used to derive the result.
- **Stub-Free:** Mocks are permitted for *testing* only. Production endpoints must use `QFSReplaySource`.
- **Audit Log:** All explanations served to users must be logged (hash + timestamp + user_id) for governance review.

***

## 7. Operational Boundaries (NEW - Critical)

### 7.1 PostgreSQL is Non-Authoritative

- **Cache Only:** PostgreSQL/Prisma stores session data, UI preferences, and read-optimized projections.
- **Never Source of Truth:** Balances, rewards, and economic state must NEVER be sourced from Prisma.
- **Sync Pattern:** QFS → Ledger → Read-Only Projection → Prisma (one-way flow).

### 7.2 AI/OpenAGI is Advisory Only

- **No Direct Effects:** AI recommendations (content moderation, signal enhancements) must route through PolicyRegistry → TreasuryEngine.
- **Bounded Outputs:** AI outputs must be discrete scalars (e.g., `safety_score: 0.0-1.0`), never direct token amounts.
- **Human-in-Loop:** High-stakes AI recommendations (ban, reward >1000 ATR) require governance approval.
- **ATLAS v14 Social Features:** Spaces recommendations, Wall ranking, Chat suggestions MAY use AI/OpenAGI to propose actions or sort views, but AI outputs MUST NEVER directly create EconomicEvents or bypass the deterministic reward formulas defined for the social layer.

### 7.3 Frontend is View + Intent Only

- **No Balance Writes:** Frontend code must never mutate `user.balance`, `wallet.atr`, or similar fields.
- **Intent Submission:** Frontend submits signed intents to ATLAS API, which forwards to QFS/AEGIS.
- **Optimistic UI:** Frontend may show optimistic updates (e.g., "pending transaction"), but must re-sync with ledger truth.

***

## 8. Implementation Contract

### 8.1 Languages & Types

- **Backend Policy:** Python (v3.11+), strictly typed with `mypy --strict`.
- **Frontend Types:** TypeScript (v5.0+), shared schemas via `ts-json-schema-generator`.
- **Type Sync:** CI must fail if `v13/policy/*.py` types diverge from `v13/ATLAS/src/lib/qfs/*.ts`.

### 8.2 Testing & Verification

- **Zero-Sim Suite:** `run_zero_sim_suite.py` must pass green (all tests, 0 mock violations in production code).
- **Coverage Threshold:** Core economics (TreasuryEngine, RewardAllocator, Guards) must have ≥90% line coverage.
- **Replay Tests:** Every explanation endpoint must have a replay equivalence test (mock vs live hashes match).

### 8.3 Deployment Gates

- **CI Checks:**
  1. Zero-Sim suite passes.
  2. Zero-Mock scanner passes (0 violations in production code).
  3. Type sync verified.
  4. AEGIS integration tests pass.
  5. PQC signature verification tests pass.

- **Staging Requirements:**
  - Deploy to staging with `EXPLAIN_THIS_SOURCE=qfs_ledger`.
  - Run E2E tests with real AEGIS API (test environment).
  - Verify explanation hashes match between staging and local replay.

- **Production Rollout:**
  - Requires ≥2 governance approvals.
  - Canary deployment (5% traffic for 24h).
  - Automated rollback if explanation hash divergence detected.

***

## 9. Governance & Amendments

### 9.1 Contract Updates

- **Proposal Required:** Any change to this contract requires a governance proposal with ≥67% approval.
- **Version Bump:** Contract version increments with each change (currently v1.3).
- **Retroactive Application:** Slices deployed before a contract update have 30 days to comply or be deprecated.

### 9.2 Emergency Override

- **Criteria:** Only in case of critical security vulnerability (e.g., PQC break, AEGIS compromise).
- **Authority:** Requires ≥3 of 5 core maintainers + AEGIS admin approval.
- **Transparency:** Emergency overrides must be logged to ledger and announced publicly within 24h.

***

## 10. Appendix: AEGIS API Integration Spec

### 10.1 Endpoints

```
POST /aegis/verify
{
  "did": "did:key:zQ3sh...",
  "signature": "0x...",
  "action": "submit_content" | "cast_vote" | "register_node"
}

Response:
{
  "verified": true,
  "user_id": "user_123",
  "reputation_tier": "veteran",  // "new" | "established" | "veteran" | "banned"
  "permissions": ["create_content", "vote"],
  "rate_limits": {
    "posts_per_hour": 10,
    "votes_per_epoch": 100
  },
  "signature": "0x...",  // AEGIS signature for QFS logging
  "timestamp": 1702584000
}
```

### 10.2 Integration Pattern

```python
# v13/core/aegis_client.py
from typing import Dict, Any

class AEGISClient:
    def verify_action(self, did: str, signature: str, action: str) -> Dict[str, Any]:
        """
        Verify user action with AEGIS.
        Raises AEGISVerificationError if denied or unreachable.
        """
        response = requests.post(
            f"{AEGIS_API_URL}/verify",
            json={"did": did, "signature": signature, "action": action},
            timeout=5  # Fail fast
        )
        
        if response.status_code != 200:
            raise AEGISVerificationError(f"AEGIS denied: {response.text}")
        
        result = response.json()
        
        # Log to QFS ledger
        ledger.log_event("aegis_verification", result)
        
        return result
```

***

## Summary of Strengthened Areas

1. **AEGIS Integration:** Mandatory for all privileged operations, fail-closed, logged to ledger.
2. **Cryptographic Verification:** PQC signatures required, Merkle proofs for content, explanation hashes auditable.
3. **Operational Boundaries:** Clear separation of QFS (truth), ATLAS (view/intent), PostgreSQL (cache), AI (advisory).
4. **Deployment Gates:** CI enforces Zero-Sim, Zero-Mock, type sync, and AEGIS integration before production.
5. **Governance:** Contract updates require supermajority approval, emergency overrides must be transparent.

This strengthened contract transforms QFS × ATLAS from "well-designed system" to **"mathematically verifiable, cryptographically auditable, governance-enforced economic platform."**
