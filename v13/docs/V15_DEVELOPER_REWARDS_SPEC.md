# v15 Developer Rewards Specification

**Version**: v15.0 Protocol Spec  
**Status**: Partial Implementation (Phase 1)  
**Foundation**: v14.0 Frozen Baseline

---

## Constitutional Statement

The Developer Rewards layer is an **additive, read-only overlay** that incentivizes protocol contributors.

- It distributes rewards from a **bounded treasury**.
- It uses **deterministic criteria** for all payouts.
- It **never** modifies v14 state or economics.

---

## 1. Bounty System

### Bounty Schema

Defined in `v13/policy/bounties/bounty_schema.py`:

- **ID**: Unique identifier (e.g., `BOUNTY-2025-001`)
- **Scope**: Detailed description of work
- **Criteria**: Deterministic, testable acceptance checks
- **Rewards**: Fixed FLX + CHR amounts
- **Stake**: Required RES deposit (anti-spam)
- **Impact**: Tier (`minor`/`feature`/`core`) for ATR boost

### BountyStateMachine

**States**: `OPEN → CLAIMED → SUBMITTED → VERIFIED → PAID`
**Failure States**: `REJECTED`, `EXPIRED`

#### Transitions

1. **OPEN → CLAIMED**:
   - Event: `bounty_claimed`
   - Action: Lock RES stake
2. **CLAIMED → SUBMITTED**:
   - Action: Link PR/commit hash
3. **SUBMITTED → VERIFIED**:
   - Check: CI green (tests, Zero-Sim, regression)
   - Check: Acceptance criteria met
   - Check: No v14 semantic drift
4. **VERIFIED → PAID**:
   - Event: `dev_bounty_paid`
   - Event: `atr_boost_applied`
   - Event: `res_stake_returned`
   - Action: Transfer rewards, unlock stake

---

## 2. Dev Rewards Treasury

A **governance-controlled, bounded wallet** for developer payouts.

### Constraints

- **Bounded**: Cannot spend more than `flx_reserve` and `chr_reserve`
- **No Minting**: Fund must be pre-filled via governance transfer
- **Alerts**: Depletion warnings at 20% and 10%

### Events

- `treasury_refill`: Governance-approved top-up
- `dev_bounty_paid`: Payout execution

---

## 3. ATR (Attention/Reputation)

**Non-transferable reputation metric** for contributors.

### Tiers & Boosts

| Impact Tier | Reward | Criteria |
|-------------|--------|----------|
| **minor** | +10 ATR | Docs, tests, small fixes |
| **feature** | +50 ATR | New modules, services |
| **core** | +100 ATR | Math, consensus, governance |

### Invariants

1. **Non-Transferable**: Cannot be sent between wallets
2. **Non-Revocable**: Cannot be removed retroactively (except via explicit slashing logic for abuse)
3. **Deterministic**: Boost amount fixed by impact tier

---

## 4. HSMF Validation

HSMF validates bounty conditions before payment.

### Validation Logic

- **CI Status**: Must be passing (all gates)
- **Zero-Sim**: Must have 0 violations
- **Regression**: Must match v14 hash (if v14 touched)
- **Criteria**: Must pass all deterministic checks

**Result**: `ValidationResult(valid=bool, reason=str)`

---

## 5. Integration & Safety

### Replayability

- Bounty lifecycle must be replayable from `bounty_*` events
- Treasury balance must be reconstructible from events

### Isolation

- Treasury is separate from v14 emission pools
- ATR is separate from v14 tokens (FLX/CHR)

**Last Updated**: 2025-12-18
