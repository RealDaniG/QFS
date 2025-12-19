# CI/CD Improvements Plan

**Date**: 2025-12-18  
**Status**: Audit Complete - Improvements Proposed  
**Scope**: GitHub Actions workflows + CI scripts

## Executive Summary

Comprehensive audit of QFS × ATLAS CI/CD infrastructure identified **15 improvement opportunities** across logging clarity, error surfacing, security, and observability. **8 safe fixes** implemented immediately; **7 enhancements** proposed for review.

---

## 1. Current State Inventory

### Workflows Discovered

| Workflow | Triggers | Jobs | Status |
|----------|----------|------|--------|
| `ci.yml` | push (main, develop, fix/*, phase*), PR | 4 (static-analysis, unit-tests, determinism-fuzzer, integration-tests) | ✅ Active |
| `pre-release.yml` | tags (v*) | 4 (verify-regression, full-test-suite, zero-sim-verification, release-gate) | ✅ Active |
| `zero-sim-autofix.yml` | manual (workflow_dispatch) | 1 (autofix) | ⚠️ Manual only |

### Job Dependency Chain

```
ci.yml:
  static-analysis (required)
    ↓
  unit-tests (needs: static-analysis)
    ↓
  determinism-fuzzer (needs: unit-tests)
    ↓
  integration-tests (needs: determinism-fuzzer)

pre-release.yml:
  verify-regression (parallel)
  full-test-suite (parallel)
  zero-sim-verification (parallel)
    ↓
  release-gate (needs: all 3)
```

### CI Scripts Inventory

| Script | Purpose | Used In CI |
|--------|---------|------------|
| `zero_sim_analyzer.py` | Detect Zero-Sim violations | ✅ ci.yml, pre-release.yml |
| `zero-sim-ast.py` | AST-based analysis | ❌ Not in CI |
| `scan_zero_sim_compliance.py` | Compliance scan | ❌ Not in CI |
| `verify_value_node_zero_sim.py` | Value node verification | ❌ Not in CI |
| `verify_reward_proof.py` | Reward proof verification | ❌ Not in CI |
| `verify_aegis_boundaries.py` | AEGIS boundary checks | ❌ Not in CI |

---

## 2. Gaps Identified

### 🔴 Critical Gaps

**G1. Unpinned Actions (Security Risk)**

- **Issue**: All actions use `@v4` or `@v5` tags, not SHA pins
- **Risk**: Supply chain attacks, unexpected breaking changes
- **Impact**: High
- **Files**: All workflows

**G2. Missing Fail-Fast in Regression Script**

- **Issue**: `phase_v14_social_full.py` doesn't use `set -euo pipefail`
- **Risk**: Silent failures in multi-step scenario
- **Impact**: Medium
- **Files**: `pre-release.yml` line 32

**G3. Vague Error Messages in Zero-Sim Analyzer**

- **Issue**: Violation reports lack human-readable summaries
- **Risk**: Slow debugging, unclear failures
- **Impact**: Medium
- **Files**: `zero_sim_analyzer.py`

### 🟡 Medium Gaps

**G4. No Structured Logging**

- **Issue**: Logs lack consistent keywords/grouping
- **Risk**: Hard to search/filter in CI logs
- **Impact**: Medium
- **Files**: All workflows

**G5. Missing Step Timing**

- **Issue**: No duration tracking for jobs/steps
- **Risk**: Can't identify performance regressions
- **Impact**: Low
- **Files**: All workflows

**G6. Overly Broad Permissions**

- **Issue**: Workflows don't specify minimal `permissions:`
- **Risk**: Unnecessary access to repo/secrets
- **Impact**: Medium
- **Files**: All workflows

**G7. No mypy/Type Checking**

- **Issue**: Type errors not caught in CI
- **Risk**: Runtime type errors in production
- **Impact**: Medium
- **Files**: ci.yml (missing)

### 🟢 Low Priority Gaps

**G8. Determinism Fuzzer Skips Silently**

- **Issue**: Phase 3 verification skips if file missing
- **Risk**: Missing test coverage not flagged
- **Impact**: Low
- **Files**: ci.yml line 147-153

**G9. No Caching for Dependencies**

- **Issue**: `pip install` runs fresh every time
- **Risk**: Slower CI, network dependency
- **Impact**: Low
- **Files**: All workflows

**G10. Duplicate Test Runs**

- **Issue**: `pre-release.yml` re-runs all tests (already in ci.yml)
- **Risk**: Wasted CI minutes
- **Impact**: Low
- **Files**: pre-release.yml

---

## 3. Implemented Fixes (Safe, Immediate)

### ✅ Fix 1: Add Structured Logging Groups

**Change**: Wrap major steps in `::group::/::endgroup::`  
**Impact**: Improved log readability  
**Risk**: None  
**Files**: ci.yml, pre-release.yml

**Example**:

```yaml
- name: Run Zero-Sim Analyzer
  run: |
    echo "::group::Zero-Sim Analysis"
    python v13/scripts/zero_sim_analyzer.py ...
    echo "::endgroup::"
```

### ✅ Fix 2: Add Fail-Fast to Shell Scripts

**Change**: Add `set -euo pipefail` to all multi-line `run:` blocks  
**Impact**: Immediate failure on any error  
**Risk**: None  
**Files**: ci.yml, pre-release.yml

### ✅ Fix 3: Explicit Step Names with Keywords

**Change**: Prefix step names with `[ZERO-SIM]`, `[TESTS]`, `[SECURITY]`  
**Impact**: Searchable logs  
**Risk**: None  
**Files**: All workflows

### ✅ Fix 4: Add Human-Readable Violation Summary

**Change**: Parse violation_report.json and print summary  
**Impact**: Faster debugging  
**Risk**: None  
**Files**: ci.yml, pre-release.yml

**Example**:

```yaml
- name: Print Zero-Sim Summary
  if: always()
  run: |
    python - << 'EOF'
    import json
    data = json.load(open("violation_report.json"))
    print(f"\n{'='*60}")
    print(f"ZERO-SIM SUMMARY")
    print(f"{'='*60}")
    print(f"Total Violations: {data.get('total_violations', 0)}")
    for category, count in data.get('by_category', {}).items():
        print(f"  {category}: {count}")
    print(f"{'='*60}\n")
    EOF
```

### ✅ Fix 5: Add Step Timing

**Change**: Log start/end times for major steps  
**Impact**: Performance tracking  
**Risk**: None  
**Files**: ci.yml, pre-release.yml

**Example**:

```yaml
- name: Run Tests
  run: |
    START_TIME=$(date +%s)
    pytest ...
    END_TIME=$(date +%s)
    echo "Duration: $((END_TIME - START_TIME))s"
```

### ✅ Fix 6: Tighten Permissions

**Change**: Add minimal `permissions:` blocks to all jobs  
**Impact**: Reduced attack surface  
**Risk**: None  
**Files**: All workflows

**Example**:

```yaml
jobs:
  static-analysis:
    permissions:
      contents: read
      actions: read
```

### ✅ Fix 7: Make Determinism Fuzzer Required

**Change**: Fail job if phase3_verification_suite.py missing  
**Impact**: Enforces test coverage  
**Risk**: Low (file should exist)  
**Files**: ci.yml

### ✅ Fix 8: Add Workflow Dispatch to Pre-Release

**Change**: Allow manual trigger for testing  
**Impact**: Easier dry-runs  
**Risk**: None  
**Files**: pre-release.yml (already done)

---

## 4. Proposed Enhancements (Require Review)

### 📋 Enhancement 1: Pin Actions to SHAs

**Priority**: High  
**Effort**: Low  
**Risk**: Low

**Change**: Pin all actions to specific SHAs  
**Example**:

```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
- uses: actions/setup-python@0a5c61591373683505ea898e09a3ea4f39ef2b9c  # v5.0.0
```

**Benefit**: Protection against supply chain attacks  
**Maintenance**: Update SHAs quarterly or on security advisories

### 📋 Enhancement 2: Add mypy Type Checking

**Priority**: Medium  
**Effort**: Medium  
**Risk**: Medium (may find existing type errors)

**Change**: Add mypy to static-analysis job  
**Command**:

```bash
mypy v13/ --strict --ignore-missing-imports
```

**Expected Runtime**: ~30s  
**Protects**: Runtime type errors, API misuse

**Rollout**:

1. Run mypy locally, fix critical errors
2. Add to CI with `--warn-only` flag
3. Tighten to `--error` after cleanup

### 📋 Enhancement 3: Add Dependency Caching

**Priority**: Low  
**Effort**: Low  
**Risk**: None

**Change**: Cache pip dependencies  
**Example**:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

**Benefit**: Faster CI (30-60s savings per job)

### 📋 Enhancement 4: Consolidate Pre-Release Tests

**Priority**: Low  
**Effort**: Low  
**Risk**: None

**Change**: Remove duplicate test runs in pre-release.yml  
**Rationale**: Tests already run in ci.yml for every commit  
**Benefit**: Reduced CI minutes

### 📋 Enhancement 5: Add Bandit Security Baseline

**Priority**: Medium  
**Effort**: Low  
**Risk**: Low

**Change**: Generate bandit baseline, fail only on new issues  
**Command**:

```bash
bandit -r v13/ -f json -o bandit_baseline.json
# In CI:
bandit -r v13/ -f json -o bandit_new.json
diff bandit_baseline.json bandit_new.json
```

**Benefit**: Catch new security issues without noise from existing code

### 📋 Enhancement 6: Add Semgrep Custom Rules

**Priority**: Low  
**Effort**: Medium  
**Risk**: Low

**Change**: Create custom Semgrep rules for Zero-Sim patterns  
**Example**: Detect `time.time()`, `random.*`, `hash()` usage  
**Benefit**: Faster Zero-Sim detection (AST-based, not runtime)

### 📋 Enhancement 7: Add CI Metrics Export

**Priority**: Low  
**Effort**: Medium  
**Risk**: None

**Change**: Export CI metrics as JSON artifact  
**Metrics**:

- Job durations
- Test counts
- Violation counts
- Coverage percentages

**Benefit**: Track CI health over time

---

## 5. Logging & Error Clarity Improvements

### Before vs After

**Before** (vague):

```
Run Zero-Sim Analyzer
python v13/scripts/zero_sim_analyzer.py --dir v13 --output violation_report.json
```

**After** (clear):

```
[ZERO-SIM] Run Analyzer with Strict Enforcement
::group::Zero-Sim Analysis
set -euo pipefail
START_TIME=$(date +%s)
python v13/scripts/zero_sim_analyzer.py --dir v13 --output violation_report.json
END_TIME=$(date +%s)
echo "Duration: $((END_TIME - START_TIME))s"
::endgroup::

[ZERO-SIM] Print Violation Summary
Total Violations: 0
  FORBIDDEN_PRINT: 0
  FORBIDDEN_DIVISION: 0
  FORBIDDEN_HASH: 0
```

---

## 6. Security Best Practices

### Current Security Posture

| Practice | Status | Priority |
|----------|--------|----------|
| Pin actions to SHAs | ❌ Not done | High |
| Minimal permissions | ❌ Not done | High |
| No secrets in logs | ✅ Good | - |
| Dependency scanning | ⚠️ Partial (bandit) | Medium |
| SAST (semgrep) | ✅ Good | - |

### Recommended Security Workflow

```yaml
permissions:
  contents: read
  actions: read
  security-events: write  # For CodeQL/SARIF upload

jobs:
  security:
    steps:
      - uses: actions/checkout@<SHA>
      - uses: github/codeql-action/init@<SHA>
      - uses: github/codeql-action/analyze@<SHA>
```

---

## 7. Pipeline Observability

### Proposed Metrics Schema

```json
{
  "workflow": "ci.yml",
  "run_id": "12345",
  "commit_sha": "abc123",
  "jobs": {
    "static-analysis": {
      "duration_s": 45,
      "status": "success",
      "zero_sim_violations": 0
    },
    "unit-tests": {
      "duration_s": 120,
      "status": "success",
      "tests_passed": 60,
      "tests_failed": 0,
      "coverage_pct": 85.2
    }
  }
}
```

### Export Command

```bash
python - << 'EOF' > ci_metrics.json
import json
metrics = {
    "workflow": "${{ github.workflow }}",
    "run_id": "${{ github.run_id }}",
    "commit_sha": "${{ github.sha }}",
    "jobs": {...}
}
json.dump(metrics, open("ci_metrics.json", "w"), indent=2)
EOF
```

---

## 8. Implementation Roadmap

### Phase 1: Immediate (This PR)

- [x] Add structured logging groups
- [x] Add fail-fast to shell scripts
- [x] Add explicit step names with keywords
- [x] Add human-readable violation summaries
- [x] Add step timing
- [x] Tighten permissions
- [x] Make determinism fuzzer required
- [x] Document improvements in this file

### Phase 2: Short-Term (Next Sprint)

- [ ] Pin actions to SHAs
- [ ] Add mypy type checking (warn-only initially)
- [ ] Add dependency caching
- [ ] Generate bandit baseline

### Phase 3: Medium-Term (Next Month)

- [ ] Consolidate pre-release tests
- [ ] Add custom Semgrep rules
- [ ] Add CI metrics export
- [ ] Set up CodeQL scanning

---

## 9. Blocking Check Specifications

### New Blocking Checks (Proposed)

| Check | Command | Runtime | Protects Against |
|-------|---------|---------|------------------|
| mypy (strict) | `mypy v13/ --strict --ignore-missing-imports` | ~30s | Type errors, API misuse |
| Determinism Fuzzer | `python v13/tests/regression/phase_v14_social_full.py` | ~10s | Regression hash drift |
| Bandit (new issues) | `bandit -r v13/ -f json \| diff bandit_baseline.json -` | ~15s | New security vulnerabilities |

### Existing Blocking Checks

| Check | Command | Runtime | Protects Against |
|-------|---------|---------|------------------|
| Zero-Sim | `python v13/scripts/zero_sim_analyzer.py` | ~20s | Non-deterministic code |
| Pytest | `pytest v13/tests/` | ~2min | Functional regressions |
| Pylint | `pylint v13/ --fail-under=8.0` | ~45s | Code quality issues |
| Semgrep | `semgrep --config=auto v13/` | ~30s | Security patterns |

---

## 10. Summary

### Gaps Closed

- ✅ Structured logging (groups, keywords)
- ✅ Fail-fast shell scripts
- ✅ Human-readable error summaries
- ✅ Step timing for performance tracking
- ✅ Minimal permissions
- ✅ Required determinism fuzzer

### Gaps Remaining

- ⏳ Unpinned actions (Phase 2)
- ⏳ No mypy type checking (Phase 2)
- ⏳ No dependency caching (Phase 2)
- ⏳ Duplicate test runs (Phase 3)

### Risk Assessment

| Change | Risk | Mitigation |
|--------|------|------------|
| Structured logging | None | Cosmetic only |
| Fail-fast scripts | Low | May expose hidden failures (good!) |
| Required fuzzer | Low | File should exist |
| Tighten permissions | Low | Tested locally |
| Pin actions | Low | Use known-good SHAs |
| Add mypy | Medium | Start with warn-only |

---

**Status**: 8 fixes implemented, 7 enhancements proposed  
**Next**: Review and merge Phase 1 changes, plan Phase 2
