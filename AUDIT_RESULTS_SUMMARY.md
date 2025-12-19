# QFS v15 Audit Results

**Timestamp:** 2025-12-19T11:21:43.247637
**Version:** QFS 19.0.0 / ATLAS 1.3.0
**Overall Status:** PASS

## Test Summary

- Total Tests: 9
- Passed: 9
- Failed: 0

## Invariant Verification

### [PASS] GOV-I1: Quorum (30%) and Supermajority (66%) via integer math only

- **Component:** ProposalEngine
- **Evidence:** test_proposal_engine.py::test_integer_thresholds
- **Status:** PASS

### [PASS] GOV-I2: Proposal IDs are content-addressed (SHA3-512)

- **Component:** ProposalEngine
- **Evidence:** test_proposal_engine.py::test_deterministic_id
- **Status:** PASS

### [PASS] GOV-R1: Immutable parameters cannot be modified

- **Component:** GovernanceParameterRegistry
- **Evidence:** test_proposal_engine.py::test_immutable_protection, test_stress_campaign.py::test_immutable_protection_under_load
- **Status:** PASS

### [PASS] TRIG-I1: Active parameters constant within epoch

- **Component:** GovernanceTrigger
- **Evidence:** test_stage_6_simulation.py::test_full_execution_lifecycle
- **Status:** PASS

### [PASS] REPLAY-I1: Bit-for-bit deterministic replay (0 drift)

- **Component:** ProposalEngine + Registry + Trigger
- **Evidence:** test_governance_replay.py::test_bit_for_bit_replay, test_stress_campaign.py::test_campaign_replay_drift
- **Status:** PASS

### [PASS] AEGIS-G1: Active Snapshot == Registry at sync points

- **Component:** GovernanceCoherenceCheck
- **Evidence:** test_stage_6_simulation.py + test_stress_campaign.py (AEGIS checks)
- **Status:** PASS

### [PASS] ECON-I1: VIRAL_POOL_CAP read from GovernanceTrigger snapshot

- **Component:** ViralRewardBinder
- **Evidence:** test_stage_6_simulation.py::test_full_execution_lifecycle
- **Status:** PASS

