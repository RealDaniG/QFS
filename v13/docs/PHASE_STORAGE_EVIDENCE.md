# QFS V13.x Decentralized Storage Evidence Index

This document maps each storage guarantee to its corresponding tests and evidence artifacts.

## Phase 0 - Spec & Freeze

### Guarantees
- [x] Data model defined (object_id, version, hash_commit, metadata fields)
- [x] Hashing algorithm choices defined (SHA3-256)
- [x] Sharding and replication rules defined (REPLICATION_FACTOR=3, NUM_SHARDS_PER_OBJECT=4)
- [x] Node eligibility rules defined (AEGIS-verified, uptime constraints)
- [x] NOD reward formula defined (bytes_stored, uptime_bucket, successful_proofs)

### Evidence Artifacts
- [x] `docs/DECENTRALIZED_STORAGE_SPEC.md` - Complete specification document

## Phase 1 - StorageEngine Stub & Mini-Network

### Guarantees
- [x] StorageEngine interfaces implemented
- [x] Deterministic write path
- [x] Deterministic read path
- [x] Storage proof generation
- [x] Object listing with deterministic sorting
- [x] In-memory node abstraction
- [x] Deterministic shard assignment
- [x] Node eligibility management

### Tests
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_register_storage_node`
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_get_eligible_nodes`
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_put_content`
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_get_content`
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_get_storage_proof`
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_list_objects`
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_deterministic_shard_assignment`
- [x] `tests/test_storage_engine.py::TestStorageEngine::test_node_metrics_update`
- [x] `tests/test_storage_engine.py::TestStorageEngineDeterminism::test_deterministic_content_hash`
- [x] `tests/test_storage_engine.py::TestStorageEngineDeterminism::test_deterministic_shard_id`
- [x] `tests/test_storage_engine.py::TestStorageEngineDeterminism::test_deterministic_node_assignment`

### Evidence Artifacts
- [x] `docs/evidence/storage/storage_determinism.json` - Verification of deterministic behavior

## Phase 2 - Node Management & AEGIS Integration

### Guarantees
- [x] Node eligibility management (registering/removing nodes)
- [x] Marking nodes as eligible/ineligible per epoch
- [x] AEGIS verification hook integration
- [x] Node join/leave/revocation handling
- [x] Deterministic shard placement changes across epochs

### Tests
- [x] `tests/test_storage_engine.py::TestStorageEngineAEGISIntegration::test_node_registration_without_aegis`
- [x] `tests/test_storage_engine.py::TestStorageEngineAEGISIntegration::test_node_registration_with_aegis`
- [x] `tests/test_storage_engine.py::TestStorageEngineAEGISIntegration::test_node_eligibility_without_aegis`
- [x] `tests/test_storage_engine.py::TestStorageEngineAEGISIntegration::test_node_eligibility_with_aegis`
- [x] `tests/test_storage_engine.py::TestStorageEngineAEGISIntegration::test_epoch_advancement`
- [x] `tests/test_storage_engine.py::TestStorageEngineAEGISIntegration::test_node_unregistration`
- [x] `tests/test_storage_engine.py::TestStorageEngineAEGISIntegration::test_node_status_management`

### Evidence Artifacts
- [x] `docs/evidence/storage/storage_node_lifecycle.json` - Documentation of epoch transitions and shard placements

## Phase 3 - Economics (ATR/NOD) & OpenAGI Hooks

### Guarantees
- [x] TokenStateBundle extension with storage metrics
- [x] ATR cost function for storage writes
- [x] Deterministic NOD reward calculation
- [x] Conservation checks (no silent inflation/leakage)
- [x] OpenAGI scoring interface
- [x] Deterministic content scoring

### Tests
- [x] `tests/test_token_state_bundle_storage.py::TestTokenStateBundleStorageExtension::test_create_token_state_bundle_with_storage_metrics`
- [x] `tests/test_token_state_bundle_storage.py::TestTokenStateBundleStorageExtension::test_create_token_state_bundle_without_storage_metrics`
- [x] `tests/test_token_state_bundle_storage.py::TestStorageEngineTokenBundleIntegration::test_update_storage_metrics_in_token_bundle`
- [x] `tests/test_token_state_bundle_storage.py::TestOpenAGIScoring::test_openagi_content_scoring`
- [x] `tests/test_token_state_bundle_storage.py::TestOpenAGIScoring::test_openagi_content_scoring_different_content`
- [x] `tests/test_token_state_bundle_storage.py::TestOpenAGIScoring::test_put_content_with_scoring`
- [x] `tests/test_storage_engine.py::TestStorageEngineEconomics::test_atr_storage_cost_calculation`
- [x] `tests/test_storage_engine.py::TestStorageEngineEconomics::test_put_content_with_atr_cost`
- [x] `tests/test_storage_engine.py::TestStorageEngineEconomics::test_nod_reward_calculation`
- [x] `tests/test_storage_engine.py::TestStorageEngineEconomics::test_storage_economics_summary`

### Evidence Artifacts
- [x] `docs/evidence/storage/storage_economics.json` - Sample ATR/NOD scenarios and conservation checks
- [x] `docs/evidence/storage/storage_economics_extended.json` - Extended ATR/NOD implementation details

## Phase 4 - Dual-Write & Consistency Testing

### Guarantees
- [x] Dual-write mode implementation
- [x] Consistency between PostgreSQL and StorageEngine
- [x] Replay capability from EQM logs
- [x] Storage state reconstruction

### Tests
- [x] `tests/e2e/test_storage_user_flow.py` - Integrated end-to-end test for full QFS flows
- [x] Dual-write consistency tests
- [x] Replay tests
- [x] State reconstruction tests

### Evidence Artifacts
- [x] `docs/evidence/storage/storage_replay.json` - Replay testing documentation
- [x] `docs/evidence/e2e/storage_user_flow_results.json` - E2E test results

## Phase 5 - Cutover, Monitoring, and Evidence Index

### Guarantees
- [x] Read-path switching capability
- [x] PostgreSQL fallback mechanism
- [x] Storage error monitoring
- [x] Shard health monitoring
- [x] Node churn monitoring

### Tests
- [x] Read path switching tests
- [x] Fallback mechanism tests
- [x] Monitoring integration tests

### Evidence Artifacts
- [x] `docs/evidence/storage/assurance/storage_replay_drill_YYYYMMDD.json` - Replay drill evidence
- [x] `docs/evidence/storage/assurance/dual_write_verification_YYYYMMDD.json` - Dual-write verification evidence
- [x] `docs/evidence/storage/assurance/dual_write_rollback_YYYYMMDD.json` - Dual-write rollback evidence
- [x] `docs/evidence/storage/assurance/node_failure_recovery_YYYYMMDD.json` - Node failure recovery evidence

## Post-Certification Operational Artifacts

### Runbooks
- [x] `docs/runbooks/storage_node_failure_recovery.md` - Node failure recovery procedures
- [x] `docs/runbooks/storage_replay_from_logs.md` - Storage replay from logs procedures
- [x] `docs/runbooks/dual_write_rollback.md` - Dual-write rollback procedures
- [x] `docs/runbooks/storage_12_month_assurance_plan.md` - 12-month assurance plan

### Alerting Configuration
- [x] `ops/monitoring/storage_alerts.yml` - Storage alerting configuration

### Automated Procedures
- [x] `scripts/run_storage_replay_drill.py` - Script for quarterly replay drills
- [x] `scripts/check_dual_write_consistency.py` - Script for monthly dual-write consistency verification
- [x] `scripts/simulate_storage_cir302_incident.py` - Script for CIR-302 incident simulation

### Dashboard Enhancements
- [x] `docs/qfs-v13.5-dashboard.html` - Enhanced dashboard with storage health and economic flow panels

### Additional E2E Tests
- [x] `tests/e2e/test_storage_economics_flow.py` - Dedicated storage economics flow test
- [x] Evidence: `docs/evidence/e2e/storage_economics_flow_results.json` - Economics flow test results