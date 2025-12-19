# v15 Timeless Protocol Specification Map

**Status**: In Design
**Baseline**: v14.0 (Autonomous-Compliant)

This document maps v15 invariants to concrete code surfaces and autonomous validation rules.

## 1. HSMF (Harmonized State Machine Framework)

| v15 Invariant | Code Surface | Autonomous Validation Rule |
|---------------|--------------|----------------------------|
| **Universal State Transition** | `v13/core/StateTransitionEngine.py` | `phase_2_guards.py`: Validate state transition atomicity |
| **Deterministic Replay** | `v13/tests/test_deterministic_replay.py` | `phase3_verification_suite`: Bit-exact replay check |
| **Fail-Closed Economics** | `v13/libs/economics/EconomicsGuard.py` | `phase_2_guards.py`: `check_res_cap`, `check_nod_power` |

## 2. Governance-Grade Actions

| v15 Invariant | Code Surface | Autonomous Validation Rule |
|---------------|--------------|----------------------------|
| **Vote Immutability** | `v13/libs/governance/NODInvariantChecker.py` | `check_vote_integirty()` (ToDo) |
| **Proposal Binding** | `v13/policy/governance/ProposalEngine.py` (Proposed) | Verify proposal hash matches execution payload |

## 3. Abuse-Resistant Positive Engagement

| v15 Invariant | Code Surface | Autonomous Validation Rule |
|---------------|--------------|----------------------------|
| **Viral Content Determinism** | `v13/atlas/scoring/ViralEngine.py` (Proposed) | Input set → Deterministic Score Check |
| **Engagement Capping** | `v13/libs/economics/EconomicsGuard.py` | `check_reward_cap()` |

## 4. Implementation Plan (HSMF Path)

1. **Stage 1 (Current)**: Enforce core economics (Done).
2. **Stage 2**: Unify `StateTransitionEngine` with `BountyStateMachine`.
3. **Stage 3**: Introduce `ViralEngine` with deterministic scoring.
