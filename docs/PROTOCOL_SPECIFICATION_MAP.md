# Protocol Specification Map

**Status: Implemented and Verified**
**Baseline: v17.0+ (Production Ready)**

This document maps protocol invariants to concrete implementation surfaces and autonomous validation rules.

## 1. Core State Machine & Determinism

| Protocol Invariant | Code Surface | Autonomous Validation Rule |
|--------------------|--------------|----------------------------|
| **Universal State Transition** | `v17/core/StateTransitionEngine.py` | `phase_2_guards.py`: Validate state transition atomicity |
| **Deterministic Replay** | `v17/tests/test_deterministic_replay.py` | `zero_sim_gate.yml`: Bit-exact replay check in CI/CD |
| **Fail-Closed Economics** | `v17/libs/economics/EconomicsGuard.py` | `phase_2_guards.py`: `check_res_cap`, `check_nod_power` |

## 2. Governance & Consensus

| Protocol Invariant | Code Surface | Autonomous Validation Rule |
|--------------------|--------------|----------------------------|
| **Vote Immutability** | `v17/libs/governance/NODInvariantChecker.py` | `check_vote_integrity()` verified in v16.1 integration |
| **Proposal Binding** | `v17/policy/governance/ProposalEngine.py` | Verified proposal hash matches execution payload via EvidenceBus |

## 3. Social & Reward Mechanics

| Protocol Invariant | Code Surface | Autonomous Validation Rule |
|--------------------|--------------|----------------------------|
| **Viral Content Determinism** | `v17/atlas/scoring/ViralEngine.py` | Input set → Deterministic Score Check enforced in `ViralSignalAddon` |
| **Engagement Capping** | `v17/libs/economics/EconomicsGuard.py` | `check_reward_cap()` enforced per-epoch |

## 4. Implementation Evolution (Completed)

1. **Phase 1-4**: Core economics and Zero-Simulation lockdown (Verified).
2. **Phase 5**: Unified `StateTransitionEngine` with `BountyStateMachine` for atomic rewards.
3. **Phase 6**: Integrated `ViralEngine` with deterministic scoring and AEGIS verification.
4. **Phase 7**: Full MOCKQPC-First architecture deployment.
