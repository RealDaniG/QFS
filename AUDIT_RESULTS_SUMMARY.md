# QFS v15 Audit Results

**Timestamp:** 2025-12-25T12:56:57.213728
**Version:** QFS 20.0.0-alpha / ATLAS 1.5.5
**Overall Status:** PASS

## Test Summary

- Total Tests: 37
- Passed: 37
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

### [PASS] HEALTH-I1: All metrics derived from deterministic, on-ledger data

- **Component:** ProtocolHealthCheck
- **Evidence:** test_protocol_health_check.py::test_health_check_deterministic_metrics
- **Status:** PASS

### [PASS] HEALTH-I2: Critical failures return non-zero exit code

- **Component:** ProtocolHealthCheck
- **Evidence:** test_protocol_health_check.py::test_health_check_aegis_fail_detection
- **Status:** PASS

### [PASS] HEALTH-I3: No external dependencies or network calls

- **Component:** ProtocolHealthCheck
- **Evidence:** test_protocol_health_check.py::test_health_check_no_external_dependencies
- **Status:** PASS

### [PASS] DASH-I1: Dashboard is read-only (no state mutations)

- **Component:** GovernanceDashboard
- **Evidence:** test_governance_dashboard.py::test_dashboard_read_only
- **Status:** PASS

### [PASS] DASH-I2: All displayed data sourced from governance modules

- **Component:** GovernanceDashboard
- **Evidence:** test_governance_dashboard.py::test_dashboard_data_accuracy_parameters
- **Status:** PASS

### [PASS] DASH-I3: PoE artifacts displayed match actual proof chain

- **Component:** GovernanceDashboard
- **Evidence:** test_governance_dashboard.py::test_dashboard_poe_artifacts_section
- **Status:** PASS

### [PASS] AUTH-S1: Session schema v1 frozen with all required fields

- **Component:** SessionModel
- **Evidence:** test_auth_schema.py::test_session_schema_version, test_session_model.py::test_session_required_fields
- **Status:** PASS

### [PASS] AUTH-S2: Session IDs are deterministic (counter + node seed + wallet hash)

- **Component:** SessionService
- **Evidence:** test_deterministic_session.py::test_deterministic_session_id
- **Status:** PASS

### [PASS] AUTH-D1: Device hash is deterministic, coarse, and low-entropy

- **Component:** DeviceBinding
- **Evidence:** test_device_binding.py::test_device_hash_deterministic
- **Status:** PASS

### [PASS] AUTH-D2: Device mismatch emits DEVICE_MISMATCH and downgrades scopes

- **Component:** DeviceBinding
- **Evidence:** test_device_binding.py::test_device_mismatch_event
- **Status:** PASS

### [PASS] AUTH-P1: Every account can have a MOCKPQC key; sessions include PQC subject

- **Component:** MOCKPQC Auth
- **Evidence:** test_mockpqc_auth.py::test_mockpqc_key_storage
- **Status:** PASS

### [PASS] AUTH-P2: MOCKPQC 'signatures' are deterministic hashes (no real crypto)

- **Component:** MOCKPQC Auth
- **Evidence:** test_mockpqc_auth.py::test_mockpqc_deterministic_sign
- **Status:** PASS

### [PASS] AUTH-E1: All auth events have auth_event_version = 1

- **Component:** EvidenceBus Auth Events
- **Evidence:** test_auth_events.py::test_auth_event_versioning
- **Status:** PASS

### [PASS] AUTH-E2: SESSION_CREATED, SESSION_REFRESHED, SESSION_REVOKED, DEVICE_BOUND, DEVICE_MISMATCH events emitted

- **Component:** EvidenceBus Auth Events
- **Evidence:** test_auth_events.py::test_session_created_event, test_auth_events.py::test_device_bound_event
- **Status:** PASS

### [PASS] AUTH-R1: Auth sessions are bit-for-bit reproducible from EvidenceBus events

- **Component:** SessionReplay
- **Evidence:** test_session_replay.py::test_session_replay_deterministic
- **Status:** PASS

### [PASS] AUTH-A1: resolveSubjectIdentity (wallet+PQC) separate from resolveTrustContext (device+MFA+OIDC)

- **Component:** AuthService
- **Evidence:** test_session_model.py::test_authority_hierarchy_separation
- **Status:** PASS

