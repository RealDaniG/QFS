# v15 Living Posts Specification

**Version**: v15.0 Protocol Spec  
**Status**: Planned Layer  
**Foundation**: v14.0 Frozen Baseline

---

## Constitutional Statement

The Living Posts layer is an **additive, read-only overlay** on v14 Wall Posts.

- It observes v14 events to compute helpfulness states.
- It distributes rewards from isolated epoch pools.
- It **never** modifies v14 posts, events, or state.

---

## 1. Helpfulness Vector \(H_p\)

For each v14 `WallPost` \( p \), v15 maintains a state vector:

$$
H_p = \{ engagement\_score,\ coherence\_score,\ reputation\_weight \}
$$

### Inputs (Read-Only)

- **v14 Events**: `post_liked`, `post_replied`, `post_quoted`, `post_pinned`
- **HSMF Outputs**: Coherence scores (0-1000)
- **ATR Tiers**: Contributor reputation from Developer Rewards layer
- **Epoch**: Deterministic block-height counters

### Properties

- **Monotonic in Evidence**: More valid engagement → higher/equal components
- **NOT Monotonic in Time**: Old posts can earn if engagement continues
- **Integer-Scaled**: All components are integers (no floats)
- **Capped**: Each component has a hard maximum to prevent blowouts

---

## 2. Deterministic Scoring Function \(f(H_p)\)

$$
score_p = f(engagement\_score,\ coherence\_score,\ reputation\_weight)
$$

### Constraints

1. **Integer Only**: Must use `CertifiedMath` and `BigNum128`
2. **Order Independent**: Result must be same regardless of event order within an epoch
3. **Composable**: Can be computed incrementally
4. **Capped**: Output must fit within `BigNum128` limits

### Candidate Form

$$
score_p = \text{CertifiedMath.imul}(
  \text{capped}(engagement\_score),
  \text{CertifiedMath.imul}(\text{capped}(coherence\_score), \text{capped}(reputation\_weight))
)
$$

---

## 3. Epoch FLX Pools

Rewards are distributed from **fixed, pre-funded pools** per epoch.

### configuration

- `FLX_POST_POOL[E]`: Total FLX available for epoch \(E\)
- **Hard Cap**: Sum of all pools is bounded
- **No Minting**: Pools must be funded via governance transfer

### Distribution Formula

For each eligible post \(p\) in epoch \(E\):

$$
reward_{p,E} = FLX\_POST\_POOL[E] \times \frac{score_{p,E}}{\sum_{j \in Active} score_{j,E}}
$$

---

## 4. PostRewardStateMachine

Manages the reward lifecycle of a post.

**States**: `NEW → ACTIVE → TAPERING → ARCHIVED`

### Transitions

- **NEW → ACTIVE**:
  - Trigger: First qualifying engagement event
  - Effect: Becomes eligible for pool rewards
- **ACTIVE → TAPERING**:
  - Trigger: Epoch count > `TAPER_START_EPOCH` OR Engagement > `ENGAGEMENT_THRESHOLD`
  - Effect: Applies `TAPER_FACTOR` decay to score
- **TAPERING → ARCHIVED**:
  - Trigger: `score_p` < `ARCHIVE_THRESHOLD`
  - Effect: Removed from active pool calculation

### Determinism

All transitions are driven by **event counts** and **epoch numbers**, never wall-clock time.

---

## 5. HSMF Engagement Validation

HSMF filters engagement to prevent gaming and ensure quality.

### Validation Rules

1. **ATR Weighting**: Engagement from high-ATR users counts more
2. **AEGIS Gating**: Tier 0 (banned) users have 0 weight
3. **Graph Analysis**: Bot-like clusters (dense mutual likes) downweighted

### Invariant
>
> Invalid or low-quality engagement **cannot increase rewards**; it can only reduce its own effective weight.

---

## 6. Integration & Safety

### Replayability

- Entire state must be reconstructible from v14 event logs + configuration
- Replay must yield identical reward distributions

### Isolation

- Living Posts state is stored separately from v14 ledger
- Rewards are emitted as **new v15 events**: `post_helpfulness_updated`, `post_reward_distributed`

**Last Updated**: 2025-12-18
