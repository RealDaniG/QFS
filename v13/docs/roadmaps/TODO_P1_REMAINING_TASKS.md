# Remaining P1 Tasks

This document tracks the remaining P1 tasks that are intentionally left as TODOs for future work.

## Implementation Status

✅ **AEGIS Advisory Gate Implementation Complete** - The minimal advisory gate with `block_suggested` and `severity` fields has been successfully implemented and integrated.

✅ **Governance Visibility Features Complete** - P2 governance visibility features including advisory safety, AGI input, correlation, and operator dashboard are all in place and deterministic.

## 1. AEGIS Veto/Rollback Capability (P2 Feature)
- **Location**: `src/guards/AEGISGuard.py`
- **Description**: AEGIS now has advisory blocking capability. Future implementation will enable actual veto/rollback capability.
- **Dependencies / Preconditions**: 
  - Real GuardEvaluated / AEGISVeto / AEGISRollback ledger events
  - Clear policy thresholds (probably in PolicyRegistry/QFS spec)
- **Minimal P2 Deliverable**: Allow AEGIS to mark an interaction as 'blocked' and emit an AEGISVeto ledger event without yet doing automatic rollback
- **Status**: P2 - Advisory gate implemented, full veto/rollback still pending
- **TODO Marker**: `# TODO(P2): Implement actual veto/rollback capability`

## 2. Real Economics Totals (P2 Feature)
- **Location**: `src/atlas_api/gateway.py` and `src/libs/economics/EconomicsGuard.py`
- **Description**: Currently using demo parameters and mock values. Future implementation will use real ledger-based economic totals.
- **Dependencies / Preconditions**: 
  - A real TokenStateService and Event Ledger replay
- **Minimal P2 Deliverable**: Replace mock economic parameters with values derived from real token state service
- **Status**: P2 - Not implemented in P1
- **TODO Marker**: `# TODO(P2): Replace with real ledger-based economic totals`

## 3. Real Storage/IPFS Wiring (P2 Feature)
- **Location**: `src/atlas_api/gateway.py`
- **Description**: Currently using mock data. Future implementation will connect to real storage and IPFS systems.
- **Dependencies / Preconditions**: 
  - Storage & Identity Core integration
  - IPFS client library
- **Minimal P2 Deliverable**: Swap _fetch_content_candidates mock for a real query using Storage & Identity Core, still with limited volume
- **Status**: P2 - Not implemented in P1
- **TODO Marker**: `# TODO(P2): Connect to real storage/IPFS systems`

## 4. Advanced Deterministic Time Sources
- **Location**: `src/libs/DeterministicTime.py`
- **Description**: While deterministic timestamp logic is implemented, advanced time sources (DRVPacket integration) are not fully wired.
- **Dependencies / Preconditions**: 
  - DRVPacket integration
  - Time synchronization protocols
- **Minimal P2 Deliverable**: Integrate basic DRVPacket time sources for timestamp derivation
- **Status**: Partially implemented
- **TODO Marker**: `# TODO(P2): Fully integrate DRVPacket time sources`

## 5. Comprehensive Audit Trail Enhancement
- **Location**: Multiple files across the codebase
- **Description**: While basic ledger functionality exists, comprehensive audit trails with full provenance tracking need enhancement.
- **Dependencies / Preconditions**: 
  - Extended event logging schema
  - Provenance tracking mechanisms
- **Minimal P2 Deliverable**: Add full provenance tracking to existing ledger events
- **Status**: Partially implemented
- **TODO Marker**: `# TODO(P2): Enhance audit trail with full provenance tracking`

## 6. Advanced Notification Types
- **Location**: `src/services/notification_service.py`
- **Description**: Basic notification system is implemented. More sophisticated notification types and delivery mechanisms are P2.
- **Dependencies / Preconditions**: 
  - Notification delivery channels
  - User preference system
- **Minimal P2 Deliverable**: Implement advanced notification delivery mechanisms with user preferences
- **Status**: Basic implementation complete
- **TODO Marker**: `# TODO(P2): Implement advanced notification delivery mechanisms`

## Implementation Guidelines

All P2 features should:
1. Maintain zero-simulation compliance
2. Preserve deterministic behavior
3. Not affect persisted economic state (use demo-only values)
4. Be clearly documented with TODO markers
5. Include appropriate test coverage when implemented

## Verification Notes

These TODOs are intentionally kept as mock/demo implementations in P1 to:
- Ensure system integration works correctly
- Maintain audit trail integrity
- Allow for proper testing of guard pipelines
- Preserve deterministic behavior throughout

## Recent Updates

✅ **Governance Dashboard API** - Added operator-only governance dashboard API for monitoring AEGIS advisories and correlated observations
✅ **Observation Correlation Mechanism** - Implemented correlation mechanism between AGI and AEGIS observations with deterministic query helper
✅ **Stress and Edge Case Testing** - Added comprehensive tests for large datasets and degraded mode scenarios