# V15/V20 Pipeline Stabilization Status

## Executive Summary

**All test pipelines are now green or stable:**

- V13: Integration-stable (frozen, documented failures only)
- V15: Fully green (production-ready)
- V17: **Fully green** (governance layer stabilized)
- V18: Fully green (Zero-Sim compatible sessions)

## Test Suite Status

| Version | Passed | Failed | Skip | XFail | Pass Rate | Status |
|---------|--------|--------|------|-------|-----------|--------|
| **V13** | 113 | 5 | 1 | 6 | 95.7% | ✅ Stable |
| **V15** | 141 | 0 | 0 | 0 | 100% | ✅ Green |
| **V17** | 22 | 0 | 0 | 0 | 100% | ✅ **Green** |
| **V18** | 50 | 0 | 0 | 0 | 100% | ✅ Green |

## Recent Stabilization Work

### V17 Governance (7 → 0 failures)

Root cause: BigNum128 type mismatches - governance used float thresholds/weights but Pydantic models require string format.

**Fixes applied:**

- `f_voting.py`: Convert weight to BigNum128 string format
- `f_execution.py`: Parse string thresholds/weights for comparisons  
- `governance_projection.py`: Parse string weights in `_generate_explanation`
- `admin_dashboard.py`: Use BigNum128 strings for GovernanceConfig
- All test files: String thresholds and assertions

### V18 Ascon Sessions (2 → 0 failures)

Root cause: SessionManager used hardcoded `current_time = 0.0` but tests used `time.sleep()`.

**Fix applied:**

- Added injectable `time_provider` to SessionManager
- Tests use logical time advancement instead of real time

## V13 Known Failures (Multi-Phase)

| Test File | Count | Root Cause |
|-----------|-------|------------|
| `test_value_node_replay_explanation.py` | 3 | Needs full ledger context |
| `test_referral_system.py` | 1 | Tier logic alignment |
| `test_coherence_referral_integration.py` | 1 | Integration wiring |

## Constraints (Active)

1. V13 failures must stay ≤5 failed, 6 xfailed
2. PQC tests remain xfail until native deps available
3. Zero-Sim, determinism, security guarantees preserved
4. Any V13 change requires full suite re-run
