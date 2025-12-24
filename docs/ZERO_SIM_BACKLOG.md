# Zero-Sim Remediation Backlog – 2025-12-24

> **Branch**: `fix/audit-remediation-2025-12-24`  
> **Generated**: 2025-12-24  
> **Status**: In Progress  

---

## Summary

| Category | Total | In Core | In Scripts | In Tests | In node_modules |
|----------|-------|---------|------------|----------|-----------------|
| `time.time()` | 32 | 6 | 0 | 7 | 19 |
| `datetime.now()` | 26 | 0 | 12 | 0 | 2 |
| **TOTAL** | 58 | 6 | 12 | 7 | 21 |

**Priority Focus**: 6 violations in core paths (high priority).

---

## Classification

### 🔴 HIGH PRIORITY (Core/Runtime Paths)

These affect determinism in production and must be fixed:

| File | Line | Pattern | Status |
|------|------|---------|--------|
| `v13/atlas/backend/lib/trust/identity.py` | 21 | Comment references time.time() | ✅ Already fixed (uses 0 default) |
| `v13/atlas/backend/lib/trust/envelope.py` | 26 | Comment references time.time() | ✅ Already fixed (uses 0 default) |
| `v13/atlas/backend/scripts/verify_intelligence_standard.py` | 39 | `int(time.time())` | ✅ FIXED (5bea483) |
| `v13/atlas/backend/scripts/verify_intelligence_layer.py` | 48 | `int(time.time() + 3600)` | ✅ FIXED (5bea483) |
| `v13/atlas/backend/tests/p2p/test_mesh.py` | 191 | `int(time.time()) + 7200` | ✅ FIXED (cd3dd84) |
| `v13/tests/mocks/mock_atlas.py` | N/A | `time.time()` | ✅ FIXED (cb02004) |
| `v13/tests/mocks/mock_openagi.py` | N/A | `time.time()` | ✅ FIXED (cb02004) |
| `v13/atlas/tests/test_auth.py` | 62,64 | `int(time.time())` | ✅ FIXED (8dc7a6a) |

### 🟡 MEDIUM PRIORITY (Scripts/Tools)

These are acceptable for operational scripts but should use deterministic helpers for evidence generation:

| File | Occurrences | Notes |
|------|-------------|-------|
| `v13/scripts/nightly_e2e.py` | 8 | Execution timing, acceptable |
| `v13/scripts/generate_full_stack_evidence.py` | 6 | Evidence timestamps, acceptable |
| `v13/scripts/scan_zero_sim_compliance.py` | 2 | Scan timing, acceptable |
| `v13/scripts/verify_value_node_zero_sim.py` | 1 | Report timestamp, acceptable |
| `v13/scripts/zero_sim_dashboard.py` | 1 | Display only, acceptable |
| `v13/scripts/generate_aes_gut_evidence.py` | 2 | Evidence timestamps, acceptable |
| `v13/scripts/build_phase3_evidence.py` | 1 | Manifest timestamp, acceptable |
| `v13/tools/run_phase2_tests.py` | 1 | Logging, acceptable |
| `v13/tools/phase3_batch1_test_cleanup.py` | 1 | Logging, acceptable |

### 🟢 LOW PRIORITY (External/node_modules)

These are in third-party code and cannot be modified:

| Location | Count |
|----------|-------|
| `v13/atlas/desktop/node_modules/...` | 19 |
| `v13/atlas/node_modules/...` | 2 |

### ⚠️ EXCEPTIONS (Build Artifacts)

These are in compiled/bundled output and should be regenerated after source fixes:

| Location | Count |
|----------|-------|
| `v13/atlas/desktop/dist/win-unpacked/resources/backend/...` | 8 |

---

## Completed Fixes

| Commit | Files Fixed | Violations | Pattern |
|--------|-------------|------------|---------|
| `cb02004` | mock_atlas.py, mock_openagi.py | 2 | `time.time()` → `det_time_now()` |
| `8dc7a6a` | test_auth.py | 1 | `time.time()` → `TEST_TIMESTAMP` |
| `5bea483` | verify_intelligence_*.py | 2 | `time.time()` → `TEST_TIMESTAMP` |
| `cd3dd84` | test_mesh.py | 1 | `time.time()` → `FUTURE_TIMESTAMP` |

**Total Fixed**: 6 files, 8 violations

---

## Recommended Next Steps

### Immediate (This PR)

1. ✅ Fix mock files (DONE)
2. ✅ Fix test_auth.py (DONE)
3. ✅ Fix verify_intelligence_*.py (DONE)
4. ✅ Fix test_mesh.py (DONE)

### Short Term (Next Sprint)

1. Regenerate `desktop/dist/` after source fixes
2. Audit scripts for evidence timestamp consistency

### Long Term

1. Consider adding Zero-Sim linter to CI gate

---

## Zero-Sim Exception Policy

Files marked as **acceptable** are operational scripts that:

- Generate human-readable reports/logs
- Are not part of the deterministic replay path
- Do not affect ledger state or consensus

If a script generates evidence that feeds into the ledger, it MUST use:

- `det_time_now()` from `v13.libs.deterministic_helpers`
- Or explicit `tts_timestamp` injection from DRV context

---

**Last Updated**: 2025-12-24T14:45:00+01:00
