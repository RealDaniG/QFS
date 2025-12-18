# v15 Event Schema Registry

**Version**: v15.0 Protocol Spec  
**Status**: Planned Registry  
**Foundation**: v14.0 Frozen Baseline

This document defines the canonical schema for all v15 events.
All v15 events are **additive**, **read-only** over v14, and **replayable**.

---

## 1. General Rules

1. **No Mutation**: v15 events MUST NOT change v14 balances or state.
2. **No Collision**: v15 event types MUST NOT conflict with v14 event names.
3. **Determinism**: All fields MUST be derived from deterministic inputs (v14 events + param config).
4. **Replayability**: All events MUST be fully reconstructible from the event log + configuration.

---

## 2. Living Posts Layer (`v15-lp`)

### `post_helpfulness_updated`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `post_helpfulness_updated` |
| `post_id` | string | ID of the v14 post |
| `epoch_id` | integer | Current epoch number |
| `engagement_score` | integer | Capped engagement metric |
| `coherence_score` | integer | HSMF coherence output (0-1000) |
| `reputation_weight` | integer | ATR-derived weight (0-1000) |
| `score_p` | integer | Final helpfulness score |
| `state` | string | Lifecycle state (NEW/ACTIVE/TAPERING/ARCHIVED) |

**Emission Conditions**:

- Whenever \(H_p\) components change due to valid engagement.
- At epoch boundaries for decay updates.

**Ordering Guarantees**:

- Invariant under reordering of engagement events *within* an epoch.
- State is a function of the aggregate set of events in the epoch.

**Replay Invariants**:

- Recomputable from v14 events + v15 coefficients.

### `post_reward_distributed`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `post_reward_distributed` |
| `post_id` | string | ID of the reward-earning post |
| `epoch_id` | integer | Epoch the reward is for |
| `wallet_id` | string | Recipient wallet address |
| `reward_amount` | integer | FLX amount distributed |

**Emission Conditions**:

- At epoch settlement for any post with `score_p > 0`.

**Replay Invariants**:

- $\sum \text{reward\_amount} == \text{FLX\_POST\_POOL}[epoch]$

---

## 3. Developer Rewards Layer (`v15-dev`)

### `bounty_claimed`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `bounty_claimed` |
| `bounty_id` | string | Unique bounty identifier |
| `actor` | string | Claimant wallet address |
| `res_staked` | integer | Amount of RES locked |

**Emission Conditions**:

- User claims an OPEN bounty with sufficient RES balance.

### `dev_bounty_paid`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `dev_bounty_paid` |
| `bounty_id` | string | Unique bounty identifier |
| `actor` | string | Recipient wallet address |
| `pr_number` | integer | GitHub PR number |
| `commit_hash` | string | Commit hash for replay |
| `flx_reward` | integer | FLX payout amount |
| `chr_reward` | integer | CHR payout amount |
| `verifier` | string | Verifier wallet address |

**Emission Conditions**:

- Verified completion of a SUBMITTED bounty.

### `atr_boost_applied`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `atr_boost_applied` |
| `actor` | string | Recipient wallet address |
| `pr_number` | integer | GitHub PR number |
| `commit_hash` | string | Commit hash for replay |
| `impact_tier` | string | `minor`, `feature`, `core` |
| `atr_delta` | integer | Reputation increase amount |

**Emission Conditions**:

- Alongside `dev_bounty_paid` or on merge of PR.

### `res_stake_returned`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `res_stake_returned` |
| `bounty_id` | string | Unique bounty identifier |
| `actor` | string | Recipient wallet address |
| `res_returned` | integer | Amount returned |
| `reason` | string | `paid`, `rejected_good_faith`, `expired` |

### `bounty_rejected`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `bounty_rejected` |
| `bounty_id` | string | Unique bounty identifier |
| `verifier` | string | Verifier wallet address |
| `reason` | string | Rejection reason |
| `res_slashed` | integer | Amount slashed (if any) |

### `treasury_refill`

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Constant: `treasury_refill` |
| `treasury_id` | string | Treasury identifier |
| `flx_added` | integer | FLX added |
| `chr_added` | integer | CHR added |
| `authorized_by` | string | Governance authority |
| `reason` | string | Refill justification |

---

## Data Dictionary & Types

- **Integers**: All amounts and scores are `BigNum128` compatible integers.
- **Strings**: UTF-8, no binary data.
- **Hashes**: SHA-256 hex strings.
- **Timestamps**: Block-based (deterministic), not wall-clock.

**Last Updated**: 2025-12-18
