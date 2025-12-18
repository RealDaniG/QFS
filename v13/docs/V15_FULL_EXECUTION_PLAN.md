# QFS × ATLAS — v15 Full Execution Plan

**Version**: v15.0  
**Status**: Protocol Planning  
**Foundation**: v14.0 (frozen, replayable checkpoint)

---

## Constitutional Statement (v15)

v15 is an **additive validation and reward layer**.

- It does **NOT** alter, reinterpret, or override any v14 semantic, economic, or social rule.
- All v14 behavior remains valid, replayable, and economically identical with v15 fully disabled.
- v15 introduces two parallel layers:
  - **Living Posts Layer** – HSMF-validated positive engagement rewards
  - **Developer Rewards Layer** – Deterministic bounties and ATR reputation boosts

Both layers consume only **pre-bounded treasuries** and are structurally read-only over v14.

---

## I. Hard Invariants

### I.1 Semantic Invariance

v15 **must NOT**:

- Modify v14 math (`CertifiedMath`, `BigNum128`, HSMF core)
- Modify v14 event meanings (Spaces, Wall, Chat)
- Modify v14 reward formulas (CHR/FLX for social actions)
- Modify v14 ledger state transitions
- Introduce implicit coupling between v14 and v15 logic

v15 **may ONLY**:

- Observe v14 events (read-only)
- Derive additional deterministic state (parallel)
- Emit **new additive events** (v15-specific)
- Distribute rewards from **isolated pools** (epoch FLX pools, Dev Rewards Treasury)

### I.2 Determinism & Zero-Sim

Every v15 output must be:

- **Deterministic and replayable** from logs
- **Integer-math only** (`CertifiedMath`, `BigNum128`)
- **Free of wall-clock dependence** (epoch-based, not timestamp-based)
- **Free of randomness** or probabilistic scoring

### I.3 Economic Isolation

- **Living Posts** draw only from `FLX_POST_POOL[epoch]`
- **Developer Rewards** draw only from `DevRewardsTreasury`
- Neither layer modifies v14 social rewards or emission schedules
- v15 introduces **no minting**; it only redistributes from pre-funded pools

---

## II. Conceptual Model: Two Parallel v15 Layers

### II.1 Parallel State Layers

v15 consists of two additive layers over v14:

**Living Posts Layer**:

- Post-level helpfulness state and scores
- Epoch-based FLX rewards from fixed pools
- HSMF-validated engagement quality
- State machine: `NEW → ACTIVE → TAPERING → ARCHIVED`

**Developer Rewards Layer**:

- Bounty-based FLX/CHR payouts
- ATR boosts via `ContributorProfile`
- Bounded Dev Rewards Treasury
- State machine: `OPEN → CLAIMED → SUBMITTED → VERIFIED → PAID` (+ failure states)

**Both layers**:

- Consume v14 events and governance decisions
- Maintain their own state (scores, lifecycle, bounty status, treasury balances, contributor profiles)
- **Never write back** into v14 state

---

## III. Living Posts Layer

### III.1 Helpfulness State \(H_p\)

For each v14 `WallPost` \( p \), v15 maintains:

$$
H_p = \{ engagement\_score,\ coherence\_score,\ reputation\_weight \}
$$

**Computed only from**:

- v14 events (likes, replies, references)
- HSMF coherence outputs
- ATR / AEGIS tiers
- Deterministic epoch counters

**Properties**:

- **Monotonic in evidence**: More valid engagement → higher or equal components
- **NOT monotonic in time**: Old posts can still earn if helpful
- **Stored as integer-scaled v15 state**, separate from `WallPost`

### III.2 Deterministic Scoring Function

$$
score_p = f(engagement\_score,\ coherence\_score,\ reputation\_weight)
$$

**Constraints on \( f \)**:

- Uses `CertifiedMath` + `BigNum128`
- No floats, no hidden normalization on external aggregates
- Composable and order-independent
- Inputs limited to: v14 social events, ATR/AEGIS tiers, HSMF coherence metrics, epoch counters
- **No time-since-creation** or velocity metrics

**Example candidate form** (to be formalized):

$$
score_p = engagement\_score \times coherence\_score \times reputation\_weight
$$

with each component defined on capped integer scales.

### III.3 Epoch FLX Pools

For each epoch \(E\):

- `FLX_POST_POOL[E]` is a **fixed, pre-allocated amount**
- For each eligible post:

$$
reward_{p,E} = FLX\_POST\_POOL[E] \times \frac{score_{p,E}}{\sum_j score_{j,E}}
$$

**Guarantees**:

- Per-epoch emission is **hard-capped** and governance-configurable
- Total FLX emitted over all epochs is bounded by \(\sum_E FLX\_POST\_POOL[E]\)
- Posts can earn across many epochs but cannot cause unbounded inflation

### III.4 PostRewardStateMachine

**States**: `NEW → ACTIVE → TAPERING → ARCHIVED`

**Drivers**:

- Engagement counts and composition
- Epoch progression
- HSMF engagement validation outputs

**Behavior**:

- **NEW**: Evidence collection, no rewards
- **ACTIVE**: Full participation in proportional reward allocation
- **TAPERING**: Deterministic decay of `score_p` to prevent permanent dominance
- **ARCHIVED**: No further rewards; state retained for replay and analytics

**Transition triggers** are deterministic formulas over counts/epochs, not wall-clock thresholds.

### III.5 HSMF Engagement Validation

HSMF validates **engagement quality**, not content truth:

- Uses ATR-weighted influence, AEGIS tier gating, and deterministic graph analysis to downweight farmed or low-trust interactions
- Enforces the invariant:

> Invalid or low-quality engagement **cannot increase rewards**; it can only reduce its own effective weight.

Living Posts reward logic always uses **HSMF-filtered engagement metrics**, not raw counts.

---

## IV. Developer Rewards Layer

### IV.1 Implemented Foundations

**Existing components**:

`v13/policy/bounties/bounty_schema.py`:

- `Bounty` dataclass (id, scope, acceptance criteria, fixed FLX/CHR reward, RES stake, impact tier)
- `BountySubmission` (contributor wallet, PR/commit links, status)
- `ContributorProfile` (ATR total, bounty history)

`v13/policy/bounties/bounty_events.py`:

- `dev_bounty_paid` – Deterministic reward payment
- `atr_boost_applied` – ATR reputation increase (non-transferable)
- `bounty_claimed` – RES stake lock
- `res_stake_returned` – Stake unlock/refund
- `bounty_rejected` – Explicit rejection outcome
- `treasury_refill` – Governance-approved refill

`v13/policy/treasury/dev_rewards_treasury.py`:

- Bounded reserves (e.g., 10,000 FLX + 5,000 CHR)
- Deterministic payouts with full event logging
- Depletion alerts at configured thresholds
- Governance-controlled refills

**Impact tiers → ATR boosts** (configurable mapping):

- `minor` → +10 ATR
- `feature` → +50 ATR
- `core` → +100 ATR

All are **v15-only, append-only, and replayable**.

### IV.2 BountyStateMachine

**Core lifecycle**:
`OPEN → CLAIMED → SUBMITTED → VERIFIED → PAID`

**Failure states**: `REJECTED`, `EXPIRED`

**Deterministic transitions**:

1. **OPEN → CLAIMED**: RES stake locked (`bounty_claimed`)
2. **CLAIMED → SUBMITTED**: PR/commit linked to the bounty
3. **SUBMITTED → VERIFIED**: CI green + acceptance criteria met + HSMF/guard checks
4. **VERIFIED → PAID**:
   - `dev_bounty_paid` from Dev Rewards Treasury
   - `atr_boost_applied` according to impact tier
   - `res_stake_returned` (or slashed for abuse, per explicit rules)

All criteria are **explicit and testable**; no subjective or hidden steps.

### IV.3 Developer HSMF Validation

HSMF validates bounty completion:

- CI status and Zero-Sim compliance
- Regression hash requirements (if the bounty touches protected paths)
- Constitutional constraints (no v14 semantic drift)

Validation returns a deterministic `ValidationResult` that gates `VERIFIED → PAID`. This ensures developer rewards remain aligned with protocol safety guarantees.

---

## V. Governance & Parameters

### V.1 Governable Parameters

**Living Posts**:

- `FLX_POST_POOL[epoch]` (per-epoch pool sizes)
- Coefficients and caps in \( f(H_p) \)
- PostRewardStateMachine thresholds (ACTIVE/TAPERING/ARCHIVED)

**Developer Rewards**:

- Dev Rewards Treasury refill amounts and policies
- ATR boost mapping per impact tier
- Rules for when bounties require governance vs maintainer approval

### V.2 Governance Process

**All changes**:

- Are proposed through `GovernanceStateMachine`
- Emit governance EconomicEvents (proposal created, voted, enacted)
- Activate at explicit epochs or "parameter snapshots", never retroactively
- Are auditable and replayable

---

## VI. Zero-Sim Contract v1.5

v1.5 **extends v1.4** by formalizing v15 behavior:

**Parallel v15 state**:

- Living Posts (vectors \(H_p\), scores, lifecycles)
- Developer Rewards (bounty state, treasury, contributor profiles)

**Pool semantics**:

- FLX epoch pools for posts
- Bounded Dev Rewards Treasury

**Replay guarantees**:

Given:

- v14 event logs
- v15 configuration
- Governance events

The system can recompute:

- All `H_p` and `score_p` values
- All `post_helpfulness_updated` / `post_reward_distributed` events
- All bounty events, treasury balances, and ATR boosts

**No v15 feature may be considered complete** unless it satisfies these replay constraints.

---

## VII. Verification & Regression

Two families of regression scenarios are required:

### VII.1 Living Posts Regression

**Multi-epoch scenario** with:

- Several posts with varied engagement
- HSMF-filtered interactions
- Lifecycle transitions (NEW → ACTIVE → TAPERING → ARCHIVED)

**Validates**:

- Scores, lifecycle transitions, reward allocations

**Asserts**:

- \(\sum\) per-epoch rewards = `FLX_POST_POOL[epoch]`
- Replay produces identical v15 state

### VII.2 Developer Rewards Regression

**Bounty lifecycle** from OPEN to PAID, including failure paths:

- RES staking
- ATR boosts
- Treasury debits and refills

**Asserts**:

- Sum of payouts ≤ initial treasury + refills
- Replay with the same events reproduces all balances and states

### VII.3 v14 Invariance

**Separately**:

- v14 regression hashes must remain **unchanged** with v15 disabled
- Replaying v14 events with and without v15 enabled must yield **identical v14 state**

---

## VIII. Standing Autonomous Continuation Plan

From this plan, an autonomous executor can safely:

### Workstream A: Living Posts Layer

**Extend the Living Posts Layer**:

- Formalize and implement \( f(H_p) \)
  - Define candidate forms
  - Implement using `CertifiedMath` + `BigNum128`
  - Test order-independence and composability
- Implement `H_p` persistence
  - Schema for storing vectors
  - Update logic on v14 events
  - Epoch-based snapshots
- Implement PostRewardStateMachine
  - State transitions (NEW → ACTIVE → TAPERING → ARCHIVED)
  - Deterministic triggers
  - Decay formulas for TAPERING
- Wire HSMF engagement validation
  - ATR-weighted influence
  - AEGIS tier gating
  - Graph analysis for farmed engagement
- Implement epoch pools
  - Pool allocation per epoch
  - Proportional reward distribution
  - Governance configuration

### Workstream B: Developer Rewards Layer

**Extend the Developer Rewards Layer**:

- Complete ATR boost integration to `ContributorProfile`
  - Wire `atr_boost_applied` events to ledger
  - Track ATR history per contributor
  - Implement governance weight calculation
- Add `BOUNTIES.md` / `CONTRIBUTORS.md` as canonical registries
  - Template for bounty creation
  - Active/completed bounty tracking
  - Contributor ATR and history
- Implement full BountyStateMachine transitions
  - Use existing events and treasury logic
  - Add HSMF validation gates
  - Implement failure paths (REJECTED, EXPIRED)
  - Add CI integration for automated verification

### Workstream C: Governance Integration

**Wire Governance**:

- Add proposal types for all governable parameters
  - Living Posts: pool sizes, scoring coefficients, thresholds
  - Developer Rewards: treasury refills, ATR mappings, approval rules
- Ensure parameter changes are logged
  - Emit governance events
  - Track activation epochs
  - Maintain parameter history
- Implement deterministic activation
  - Epoch-based activation (not immediate)
  - Snapshot-based parameter application
  - Replay compatibility

### Workstream D: Verification & Testing

**At every step, maintain**:

- **v14 invariants and regression hashes**
  - Run v14 regression suite
  - Verify hashes unchanged
  - Test v14 state isolation
- **Zero-Sim compliance**
  - No new violations
  - All v15 code passes analyzer
  - Deterministic event emission
- **Economic isolation**
  - No cross-pool leakage
  - No minting
  - Treasury balance assertions
- **Full explainability**
  - Trace all rewards to events
  - Document all state transitions
  - Provide audit trails

---

## IX. Implementation Readiness

This yields a **timeless, implementation-ready v15 protocol layer** that unifies Living Posts and Developer Rewards without compromising the deterministic, constitutional core of QFS × ATLAS.

**Current Status**:

- ✅ Developer Rewards foundation implemented (schema, events, treasury)
- ⏳ Living Posts foundation (design complete, implementation pending)
- ⏳ Governance integration (design complete, implementation pending)
- ⏳ Regression scenarios (design complete, implementation pending)

**Autonomous Continuation**:

An autonomous executor can proceed with any workstream independently, as long as:

1. v14 invariants are preserved
2. Zero-Sim compliance is maintained
3. Economic isolation is enforced
4. All changes are replayable and explainable

**No timelines, no phases** – only protocol-level intent and standing workstreams that can be executed in any order while maintaining constitutional guarantees.

---

**Status**: Protocol specification complete  
**Foundation**: v14.0 (frozen, replayable)  
**Next**: Execute workstreams autonomously
