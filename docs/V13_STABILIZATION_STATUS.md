# V13 Stabilization Status

## Current Status: Integration Stabilization In Progress

| Metric | Count |
|--------|-------|
| **Passed** | 98 |
| **Failed** | 20 |
| **Skipped** | 1 |
| **XFailed** | 6 |
| **Total Discovered** | 719 |

## Subsystem Status

### ✅ Fully Green

- HD Derivation (9 tests)
- Appeals Workflow (4 tests)
- Bounty State Machine (6 tests)
- Core Math (9 tests)
- Appeals Scoring (3 tests)
- Memory Hygiene (3 tests)

### 🔶 XFailed (Documented)

- **PQC Provider Consistency Shim** (6 tests)
  - Reason: Require native `AES256_CTR_DRBG` and LegacyPQC methods unavailable in CI
  - TODO: Full PQC provider mock or native lib installation

### ❌ Remaining Failures

| Subsystem | Count | Root Cause |
|-----------|-------|------------|
| OpenAGI DM Integration | 8 | DM service API mismatch |
| Value Node Replay | 3 | Explanation path requires full ledger |
| Keystore Manager | 2 | File path/permission issues |
| Referral System | 1 | Tier calculation mismatch |
| Others | 6 | Various integration issues |

## Recent Fixes

1. **derive_creator_keypair** - Implemented empty function body
2. **artistic_policy.py** - Removed duplicate classes, fixed BigNum128 JSON serialization
3. **test_appeals_workflow.py** - Added required timestamp arguments
4. **LedgerWriter** - Fixed value type (int -> string) for GenesisEntry
5. **test_system_creator_wallet.py** - Updated expected addresses to qfs1 format
6. **BountyStateMachine** - Accept int or BigNum128 in claim_bounty

## Exit Conditions

Target: ≤10 failures with all remaining documented as multi-phase issues.

- [x] 100% test discovery (719 tests)
- [/] ≤10 remaining failures
- [ ] All remaining failures documented
- [ ] V13_STABILIZATION_STATUS.md complete
