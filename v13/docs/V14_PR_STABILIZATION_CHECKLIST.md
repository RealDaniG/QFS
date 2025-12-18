# v14 Social Layer - PR Stabilization Checklist

**Version**: v14.0-social-layer  
**Status**: Pre-Merge  
**Date**: 2025-12-18

## PR Acceptance Criteria

Only accept changes that:

- ✅ Fix bugs, test gaps, or doc mismatches
- ✅ Improve Zero-Sim compliance
- ✅ Add missing test coverage
- ❌ **DO NOT** alter social semantics without contract update
- ❌ **DO NOT** change economics without contract update
- ❌ **DO NOT** break Zero-Sim v1.4 guarantees

## Pre-Merge Checklist

### 1. CI Pipeline

- [ ] All tests pass (Spaces, Wall, Chat)
- [ ] Zero-Sim analyzer: 0 violations
- [ ] Linting passes
- [ ] Type checking passes
- [ ] No regressions in existing tests

### 2. Documentation

- [ ] `ATLAS_SOCIAL_OVERVIEW.md` updated
- [ ] `ATLAS_ECONOMIC_EVENTS.md` updated
- [ ] `ZERO_SIM_QFS_ATLAS_CONTRACT.md` v1.4 finalized
- [ ] Module READMEs complete (Spaces, Wall, Chat)
- [ ] API documentation current

### 3. Test Coverage

- [ ] Spaces: 20+ tests passing
- [ ] Wall Posts: 20+ tests passing
- [ ] Chat: 20+ tests passing
- [ ] Integration tests passing
- [ ] Regression tests passing

### 4. Zero-Sim Compliance

- [ ] `v13/atlas/spaces/`: 0 violations
- [ ] `v13/atlas/wall/`: 0 violations
- [ ] `v13/atlas/chat/`: 0 violations
- [ ] `v13/core/CoherenceEngine.py`: 0 violations (sort key fixed)
- [ ] `v13/core/HSMF.py`: 0 violations
- [ ] `v13/libs/integration/StateTransitionEngine.py`: 0 violations

### 5. Economic Events

- [ ] All 11 event types documented
- [ ] CHR/FLX amounts verified
- [ ] Event emission tested
- [ ] Reward calculations deterministic

## Post-Merge Actions

### 1. Release Tagging

```bash
git tag -a v14.0-social-layer -m "v14 Social Layer: Spaces, Wall Posts, Chat"
git push origin v14.0-social-layer
```

### 2. Contract Update

**Update** `ZERO_SIM_QFS_ATLAS_CONTRACT.md`:

- Add v1.4 social layer specification
- Document economic event guarantees
- Add deterministic ordering rules
- Include regression hash

### 3. Documentation

**Create/Update**:

- `v13/docs/ATLAS_SOCIAL_ECONOMICS.md` - Economic event tables
- `v13/docs/V14_RELEASE_NOTES.md` - Release summary
- `v13/docs/REGRESSION_HASHES.md` - Add v14 hash

### 4. Regression Hash

**Generate** from `phase_v14_social_full.py`:

```bash
python v13/tests/regression/phase_v14_social_full.py > v14_trace.log
sha256sum v14_trace.log > v14_regression_hash.txt
```

**Expected Output**:

```
<hash>  v14_trace.log
```

**Commit** `v14_regression_hash.txt` to repo.

## Economic Event Summary (for docs)

| Event | Module | Token | Amount | Trigger |
|-------|--------|-------|--------|---------|
| space_created | Spaces | CHR | 0.5 | Create space |
| space_joined | Spaces | CHR | 0.2 | Join space |
| space_spoke | Spaces | CHR | 0.1 | Speak in space |
| space_ended | Spaces | CHR | 0.3 | End space |
| post_created | Wall | CHR | 0.5 | Create post |
| post_quoted | Wall | CHR | 0.3 | Quote post |
| post_pinned | Wall | CHR | 0.2 | Pin post |
| post_reacted | Wall | FLX | 0.01 | React to post |
| conversation_created | Chat | CHR | 0.3 | Create conversation |
| message_sent | Chat | CHR | 0.1 | Send message |
| message_read | Chat | FLX | 0.01 | Read message |

**Total**: 11 events, 3 modules

## Zero-Sim Guarantees (v1.4)

1. **Deterministic IDs**: All entities use `DeterministicID.from_string()`
2. **Sorted Iterations**: All loops over collections use `sorted()`
3. **BigNum128 Economics**: All rewards use `BigNum128` precision
4. **No Randomness**: No `random`, `time.time()`, or `datetime.now()`
5. **PQC Logging**: All operations logged with PQC metadata
6. **Atomic Updates**: StateTransitionEngine ensures 5-token atomicity

## Review Guidelines

### For Reviewers

**Focus Areas**:

1. Zero-Sim compliance (no violations)
2. Deterministic behavior (replay consistency)
3. Economic correctness (BigNum128, no floats)
4. Test coverage (>90% for new code)
5. Documentation completeness

**Red Flags**:

- Any `time.time()`, `random`, or `datetime.now()`
- Unsorted iterations over dicts/sets
- Float arithmetic in economics
- Missing tests for new features
- Undocumented economic events

### For Contributors

**Before Submitting PR**:

1. Run `zero_sim_analyzer.py` on changed files
2. Run full test suite locally
3. Update documentation
4. Add tests for new features
5. Verify deterministic replay

## Merge Criteria

**All must be ✅**:

- [ ] CI green
- [ ] Zero-Sim clean (0 violations)
- [ ] Tests passing (60+ tests)
- [ ] Documentation updated
- [ ] Economic events verified
- [ ] Regression hash generated
- [ ] Contract v1.4 finalized

---

**Status**: Ready for review and merge
