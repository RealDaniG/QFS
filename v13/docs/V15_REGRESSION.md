# v15 Regression Scenarios

**Version**: v15.0 Protocol Spec  
**Status**: Planned Tests  
**Foundation**: v14.0 Frozen Baseline

---

## Overview

v15 adds parallel logic layers. These regressions ensure v15 behaves deterministically without affecting v14.

---

## 1. Living Posts Regression (`[V15-LP]`)

**Scenario**: Multi-Epoch Engagement
**File**: `v13/tests/regression/phase_v15_living_posts.py` (Planned)

### Steps

1. **Setup**: Initialize v14 ledger + v15 `FLX_POST_POOL` (e.g., 1000 FLX/epoch).
2. **Epoch 1**:
   - User A posts P1.
   - User B likes P1 (+ engagement).
   - *Check*: P1 state `NEW → ACTIVE`.
3. **Epoch 2**:
   - User C (high ATR) replies to P1.
   - User D (low ATR) likes P1.
   - *Check*: Score updates reflect ATR weighting.
   - *Check*: Reward distributed = 1000 FLX (proportional).
4. **Epoch 10** (Jump):
   - *Check*: P1 enters `TAPERING` state (score decays).
5. **Replay**:
   - Re-run full sequence.
   - Assert final scores and balances match exactly.

### Invariants

- $\sum \text{Rewards} == \text{Pool Size}$
- v14 ledger balances unchanged (except for strictly v14 rewards).

---

## 2. Developer Rewards Regression (`[V15-DEV]`)

**Scenario**: Bounty Lifecycle
**File**: `v13/tests/regression/phase_v15_dev_rewards.py` (Planned)

### Steps

1. **Setup**: Treasury seeded with 10,000 FLX.
2. **Bounty Creation**: BOUNTY-001 created (Reward: 500 FLX).
3. **Claim**: User Dev1 stakes 50 RES.
   - *Check*: RES locked in v15 state.
4. **Submission**: Dev1 submits PR #123.
5. **Verification**:
   - Simulate CI pass.
   - Verify acceptance.
6. **Payment**:
   - *Check*: Treasury balance 10,000 → 9,500 FLX.
   - *Check*: Dev1 receives 500 FLX + ATR boost.
   - *Check*: RES stake returned.
7. **Replay**:
   - Assert exact recreation of events.

---

## 3. v14 Invariance Check (`[V14-CORE]`)

**Scenario**: Baseline Stability

### Checks

1. **Hash Match**: Run `phase_v14_social_full.py` with `V15_ENABLED=true`.
   - Assert hash matches `v14_regression_hash.txt`.
2. **Cross-Check**: Run `phase_v14_social_full.py` with `V15_ENABLED=false`.
   - Assert v14 state is **identical** to run with V15 enabled.

**Last Updated**: 2025-12-18
