# TRANSMISSION #6: v15 EXECUTION PLAN LOCKED

**Date**: 2025-12-18  
**Subject**: v15 Protocol Specification & v14 Frozen Baseline  
**Status**: ACTIVE

---

## Executive Summary

The **v15 Spec is locked**.

- **v14 (Social Layer)** is now a frozen, replayable baseline.  
- **v15 (Living Posts + Dev Rewards)** is a parallel, additive layer.  
- **Documentation** is fully synchronized.

We move from "planning phases" to **Standing Autonomous Workstreams**.

---

## 1. The v14 Frozen Baseline

v14 is complete and hardened.

- **Social Modules**: Spaces, Wall, Chat live.
- **Invariants**: 100% deterministic, 0 Zero-Sim violations.
- **Security**: Regression hash `v14_regression_hash.txt` is CI-gated.

**Rule**: No changes to v14 semantics or economics are permitted.

---

## 2. The v15 Parallel Layer

v15 is an **additive overlay** that reads v14 events but maintains its own state.

### A. Living Posts

- **Concept**: Deterministic "helpfulness" scores for posts.
- **Mechanism**: Epoch-based FLX pools (pre-funded, bounded).
- **Validation**: HSMF filters engagement (ATR-weighted) to prevent farming.

### B. Developer Rewards

- **Concept**: Deterministic bounties for protocol contributors.
- **Mechanism**: Fixed FLX/CHR rewards + ATR reputation boosts.
- **Treasury**: Bounded, governance-controlled reserve.

---

## 3. Standing Workstreams

We execute v15 via four autonomous tracks:

- **Workstream A**: Living Posts (Scoring, Pools, State Machine)
- **Workstream B**: Dev Rewards (Bounties, ATR, Verification)
- **Workstream C**: Governance (Parameters, Proposals)
- **Workstream D**: Verification (Regressions, Invariants)

---

## 4. Documentation

The documentation surface is now fully aligned:

- **Protocol**: [`V15_PROTOCOL_SPEC.md`](../V15_PROTOCOL_SPEC.md)
- **Specs**: [`V15_LIVING_POSTS_SPEC.md`](../V15_LIVING_POSTS_SPEC.md), [`V15_DEVELOPER_REWARDS_SPEC.md`](../V15_DEVELOPER_REWARDS_SPEC.md)
- **Registries**: [`BOUNTIES.md`](../../../BOUNTIES.md), [`CONTRIBUTORS.md`](../../../CONTRIBUTORS.md)
- **Roadmap**: [`ROADMAP.md`](../ROADMAP.md)

---

**Directive**: Proceed with autonomous execution of Workstreams A-D in any order, always preserving v14 invariants.

*QFS × ATLAS Core Team*
