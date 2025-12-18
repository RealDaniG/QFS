# v15 Non-Goals & Protected Areas

**Version**: v15.0-governance-hsmf  
**Purpose**: Explicit boundaries to protect v14 stability  
**Status**: Planning

## Overview

v15 adds governance state machines and HSMF integration **on top of** v14, not by modifying it. This document defines what v15 **MUST NOT** change to preserve v14 as a frozen, replayable checkpoint.

## Absolute Non-Goals

### 1. No Changes to Math Core

**Protected**:

- `v13/libs/CertifiedMath.py`
- `v13/libs/BigNum128.py`
- `v13/libs/BigNum128_fixed.py`

**Rationale**: Math core is the foundation of determinism. Any change risks breaking Zero-Sim compliance across the entire system.

**Exception Process**: If a critical bug is found, it requires:

1. Separate hotfix PR with full regression suite
2. Update to Zero-Sim contract (v1.5+)
3. New regression hash for v14
4. Backport to v14 branch before v15 merge

### 2. No Changes to v14 Social Semantics

**Protected**:

- `v13/atlas/spaces/` - All files
- `v13/atlas/wall/` - All files
- `v13/atlas/chat/` - All files

**Rationale**: v14 social layer is tagged, tested, and regression-hashed. Changes would invalidate the v14 checkpoint.

**Exception Process**: Bug fixes only, and they require:

1. Update `REGRESSION.md` with reason for change
2. Regenerate `v14_regression_hash.txt`
3. Document in `ZERO_SIM_QFS_ATLAS_CONTRACT.md` (v1.4.1+)
4. Add regression test for the bug

### 3. No Changes to v14 Economics

**Protected**:

- All reward amounts (0.5 CHR, 0.2 CHR, 0.1 CHR, etc.)
- Event emission logic
- Token types (CHR/FLX)

**Rationale**: Economic parameters are part of the v14 contract. Changes would break economic replay.

**v15 Approach**: Add governance-controlled parameter updates, but:

- Default values match v14
- Updates are opt-in via governance proposals
- v14 behavior is preserved when governance is disabled

### 4. No Changes to StateTransitionEngine Atomicity

**Protected**:

- `v13/libs/integration/StateTransitionEngine.py`
- 5-token atomic update guarantee
- Deterministic state transitions

**Rationale**: StateTransitionEngine is the core of state management. Changes risk breaking atomicity guarantees.

**v15 Approach**: Extend with governance state tracking, but:

- Preserve existing atomic update semantics
- Add governance state as a separate concern
- No changes to token state update logic

### 5. No Changes to Zero-Sim Contract v1.4

**Protected**:

- Deterministic ID generation
- Sorted iterations
- BigNum128 precision
- No randomness/time/floats
- PQC logging

**Rationale**: Zero-Sim v1.4 is the compliance baseline for v14.

**v15 Approach**:

- Extend to v1.5 with governance-specific rules
- v1.4 remains valid for v14 modules
- No retroactive changes to v1.4 compliance

## Allowed Changes (Additive Only)

### 1. New Modules

**Allowed**:

- `v13/libs/governance/GovernanceStateMachine.py` (new)
- `v13/libs/guards/GuardStateMachine.py` (new)
- `v13/libs/guards/AEGISGuardStateMachine.py` (new)

**Constraint**: Must not import or modify v14 social modules

### 2. PolicyRegistry Integration

**Allowed**:

- Extend `v13/policy/PolicyRegistry.py` with HSMF awareness
- Add governance proposal tracking

**Constraint**:

- Preserve existing policy behavior
- New features are opt-in
- No breaking changes to existing policy API

### 3. Optional HSMF Validation

**Allowed**:

- Add optional HSMF validation to social event emission
- C_holo-based reward scaling (opt-in)

**Constraint**:

- Default behavior matches v14 exactly
- HSMF validation is disabled by default
- Enabled via explicit configuration flag

### 4. Governance State Tracking

**Allowed**:

- Add governance proposal state to StateTransitionEngine
- Track governance events separately

**Constraint**:

- No changes to existing token state updates
- Governance state is orthogonal to economic state
- Replay of v14 scenarios works unchanged

## Change Review Process

### For Any Change to Protected Areas

1. **Justification**: Document why change is necessary
2. **Impact Analysis**: Assess impact on v14 replay
3. **Contract Update**: Update Zero-Sim contract if needed
4. **Regression Update**: Regenerate hash if v14 behavior changes
5. **PR Review**: Require 2+ reviewers for protected area changes
6. **Test Coverage**: Add regression test for the change

### For Additive Changes

1. **Isolation**: Prove change doesn't affect v14 modules
2. **Opt-In**: Ensure new features are disabled by default
3. **Documentation**: Update v15 roadmap with change
4. **Test Coverage**: Add tests for new functionality

## Enforcement

### CI Checks

- **File Watch**: Fail CI if protected files are modified without justification
- **Regression Hash**: Fail if hash changes without `REGRESSION.md` update
- **Contract Version**: Fail if v1.4 compliance is broken

### Branch Protection

- **main**: Require "v14 Protected Areas" check to pass
- **feat/v15-***: Require isolation proof before merge to main

## Rollback Plan

If v15 changes accidentally break v14:

1. **Immediate**: Revert the breaking commit
2. **Verify**: Re-run v14 regression suite
3. **Document**: Add to `SECURITY_NOTES.md` incident log
4. **Prevent**: Add CI check to prevent recurrence

---

**Status**: Enforced starting v15 development  
**Review**: Before any v15 merge to main
