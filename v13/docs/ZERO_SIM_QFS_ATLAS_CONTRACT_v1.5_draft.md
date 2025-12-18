# Zero-Sim QFS × ATLAS Contract v1.5 [DRAFT]

**Version**: v1.5 DRAFT  
**Status**: Proposal  
**Extends**: [v1.4](ZERO_SIM_QFS_ATLAS_CONTRACT.md)

---

## I. Preamble

This contract extends the v1.4 Zero-Sim definition to cover the **v15 additive layers** (Living Posts and Developer Rewards). It enforces determinism, replayability, and economic isolation for these new parallel systems.

**v1.4 remains in full force** for the v14 Social Layer. v1.5 adds constraints for v15.

---

## II. v15 Parallel State Extension

v15 introduces state that is **parallel** to the v14 ledger:

1. **Living Posts State**: Helpfulness vectors \(H_p\) and scores.
2. **Developer Rewards State**: Bounty statuses, treasury balances, contributor profiles.

### Guarantee II.1: Read-Only Baseline

v15 systems must be **read-only** with respect to v14 state. They cannot mutate v14 ledger balances, posts, or events.

### Guarantee II.2: Independent Determinism

v15 state must be fully deterministic and replayable given:

- The v14 event log.
- The v15 configuration (governance parameters).
- The v15 event log (new additive events).

---

## III. Pool Semantics

### Guarantee III.1: Pre-Funded Isolation

v15 rewards must be drawn from **isolated, pre-funded pools**:

- `FLX_POST_POOL` (Epoch-based)
- `DevRewardsTreasury` (Bounded wallet)

No minting is permitted by v15 logic.

### Guarantee III.2: Bounded Emissions

Total rewards distributed by v15 in any epoch \(E\) cannot exceed the pre-allocated pool size for \(E\).

---

## IV. Order Invariance (Living Posts)

### Guarantee IV.1: Intra-Epoch Invariance

For Living Posts, the scoring function \(f(H_p)\) and reward allocation must be invariant to the order of events **within a single epoch**, provided the set of events and their parameters remains constant.

*Exception: Where v14 semantics naturally impose order (e.g., replies require parents), that order is respected.*

---

## V. Replay Guarantees

The system guarantees that:

1. **Full V15 Reconstruction**: Any node possessing the full historical log and v15 configuration can reconstruct the exact v15 state (scores, balances, bounties).
2. **Cross-Version Stability**: Replaying the history with v15 DISABLED yields the exact v14 state defined by Contract v1.4.

---

**Signed (Draft)**: QFS × ATLAS Core Team  
**Date**: 2025-12-18
