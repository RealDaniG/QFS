# QFS V13.8 – User as Value Node & Content-NFT Model (Skeleton)

## 1. Overview

This document defines the **user as a deterministic value node** and **content as an NFT-style, content-addressed object** in QFS V13.8.

The goal is to ensure that:

- Every user has a well-defined, ledger-backed `UserState`.
- Every piece of content is treated as a content-addressed, NFT-style object.
- All state evolution is deterministic, replayable, and governed by Zero-Sim and constitutional guards.

> NOTE: This is a **skeleton** for V13.8. Exact formulas and policy constants are filled in other specs (economics, guards, coherence).

---

## 2. User State Model

`UserState` is the canonical representation of a user as a value node. Field names and types (conceptual):

- `user_id: str`
  - Pseudonymous identifier; stable across the system.
- `balances: Dict[str, BigNum128]`
  - Asset balances per token symbol (e.g. `{"QFS": ..., "ATR": ...}`).
- `atr_balance: BigNum128`
  - Dedicated ATR position for the user.
- `flx_balance: BigNum128`
  - Dedicated FLX position for the user.
- `coherence_metrics: Dict[str, float]`
  - Aggregated coherence / ΨSync metrics for the user. Keys may include dimensions such as `"semantic"`, `"temporal"`, etc.
- `governance_footprint: Dict[str, Any]`
  - Summary of governance activity (e.g. counts or references to proposals authored, votes cast, delegations).
- `last_update_block: int`
  - Block height or ledger index at which this state was last updated.

> TODO: Link each field to the authoritative engine/spec (TreasuryEngine, RewardAllocator, CoherenceEngine, GovernanceEngine) without redefining their internals here.

---

## 3. Content-NFT Model

Content is treated as an NFT-style, content-addressed object. A **content-NFT** is defined by:

- `content_id: str`
  - Deterministic identifier, e.g. `SHA256(canonical_payload_and_metadata)`.
- `creator_id: str`
  - `user_id` of the creator.
- `version: int`
  - Monotonic version number (starting at 1). `content_id` is bound to the canonical representation; updates are modelled via versioning and events.
- `cid: str`
  - Content-addressed storage reference (e.g. IPFS CID). Used as an opaque reference; QFS consensus depends only on this hash/address, not the live external content.
- `content_type: str`
  - Logical type (e.g. `"post"`, `"comment"`, `"media"`).
- `created_at: int | str`
  - Ledger-timestamp or block index; representation is deterministic and policy-defined.

### 3.1 Canonical Serialization

Content IDs and hashes MUST be computed from a **canonical representation** of payload and metadata, for example:

- JSON encoding with:
  - Sorted keys (`sort_keys=true`).
  - UTF-8 encoding.
  - Stable separators (e.g. `separators=(",", ":")`).
- Structure similar to:

```json
{
  "payload": { /* logical content */ },
  "metadata": { /* creator_id, content_type, tags, etc. */ }
}
```

The exact canonicalization details are enforced by the implementation and verified by tests.

> TODO: Link to the canonical serialization helper(s) used in the implementation once finalized.

---

## 4. Event Taxonomy (Skeleton)

This section lists the **key event types** that drive user value-node evolution and content-NFT lifecycle.

| event_type         | actor(s) | primary_keys                   | state_fields_updated                     |
|--------------------|----------|--------------------------------|------------------------------------------|
| `ContentCreated`   | user_id  | user_id, content_id           | content index, user footprint            |
| `InteractionCreated` | user_id | user_id, content_id           | coherence_metrics, engagement counters   |
| `RewardAllocated`  | system   | user_id, (content_id optional) | balances, atr_balance, flx_balance       |
| `GovernanceVoteCast` | user_id | user_id, proposal_id          | governance_footprint                     |

### 4.1 Event Cross-Links (initial)

For each event type we track the **intended implementation and tests** (to be expanded as V13.8 work proceeds):

- `ContentCreated`
  - Impl: `TODO: qfs/ledger/events.py` (or equivalent ledger event module)
  - Tests: `tests/value_node/test_content_id_determinism.py`
- `InteractionCreated`
  - Impl: `TODO: qfs/ledger/events.py`, `TODO: coherence/engine` modules
  - Tests: `TODO: tests/value_node/test_value_node_replay.py`
- `RewardAllocated`
  - Impl: `TODO: economics/rewards.py` (TreasuryEngine, RewardAllocator)
  - Tests: `TODO: tests/value_node/test_value_node_replay.py` and existing economics test suites
- `GovernanceVoteCast`
  - Impl: `TODO: governance/events.py`
  - Tests: `TODO: tests/governance/test_vote_flow.py` (future work)

> NOTE: Paths are placeholders until cross-checked with actual module layout. They serve as anchors for V13.8 verification work.

---

## 5. Replayability & Zero-Sim Requirements

All `UserState` and content-NFT state **MUST** be reconstructible from:

1. The ordered ledger event log (including the events listed above and others defined in related specs).
2. Deterministic policies and constants (economics, guards, coherence), defined in dedicated specs.

Zero-Sim / replay requirements:

- No use of wall-clock time or RNG in consensus/state-transition logic beyond injected, test-controlled clocks where explicitly allowed.
- Replaying the same event trace from the same genesis state MUST produce identical `UserState` and content-NFT state.
- Guard and AEGIS decisions (approve/flag/block) MUST be functions only of:
  - Event data.
  - Deterministic policies and immutable config.

### 5.1 Verification Artifacts (initial)

As of the V13.8 spec skeleton, the following tests are planned/introduced to verify this model:

- `tests/value_node/test_content_id_determinism.py`
- `tests/value_node/test_value_node_replay.py`
- `tests/value_node/test_value_graph_ref.py`

These tests are non-exhaustive; they are the first verification slice for the "user as value node" and content-NFT model and will be extended as V13.8 progresses.

### 5.2 Value Graph Reference Implementation

For V13.8, a **reference-only value graph helper** is provided to exercise
value-node and content-NFT semantics without touching core economics or
ledger state:

- Implementation:
  - `src/value_graph_ref.py`
- Tests:
  - `tests/value_node/test_value_graph_ref.py`
  - `tests/value_node/test_value_node_replay.py`

This helper builds an in-memory graph of `UserNode` and `ContentNode`
instances and associated edges (`InteractionEdge`, `RewardEdge`,
`GovernanceEdge`) from an ordered event list. It is deterministic and
side-effect-free and is intended purely for replay-based validation and
observability.
