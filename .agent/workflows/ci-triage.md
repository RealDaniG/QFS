---
description: Post-CI triage and automated issue resolution for QFS × ATLAS
---

# QFS × ATLAS – Post-CI Triage and Next Steps

## Context

- **Zero-Sim Contract v1.4** is active and enforced, including ATLAS v14 Social Layer guarantees (deterministic IDs, economic wiring for social actions, unified social regression, canonical contracts, and AI advisory-only).
- The **ATLAS v14 Social Layer PR** ("ATLAS v14 Social Layer – Deterministic Spaces/Wall/Chat + Canonical Contracts") is open and feature-complete.
- CI/GitHub Actions pipelines have been fixed by aligning script paths (e.g., moving `zero_sim_analyzer.py` to `v13/scripts/`), and Zero-Sim tooling is now part of the enforced flow.

## Task

Given that **new CI issues or regressions may appear** (for current PRs or future branches), perform the following steps **automatically and iteratively**, without changing math core or social semantics unless strictly necessary.

## Step 1: Identify the Failing Checks

Inspect which GitHub Actions jobs are failing:

- Zero-Sim Analyzer / Auto-fix
- Test suite (`pytest`)
- Type sync / mypy
- AEGIS/PQC integration tests

Extract exact error messages and failing commands.

**Actions**:

```bash
# Check GitHub Actions status
# Navigate to: https://github.com/RealDaniG/QFS/actions

# Or use GitHub CLI
gh run list --branch <branch-name> --limit 5
gh run view <run-id> --log-failed
```

## Step 2: Classify the Issue

For each failure, decide whether it is:

### Infrastructure-level

- Paths, scripts, CI config, missing files
- **Example**: `FileNotFoundError: v13/scripts/zero_sim_analyzer.py`

### Contract-level

- Schemas out of sync with code or docs
- **Example**: Missing `SpacesEvent` in canonical schema

### Behavior-level

- Tests reveal a real semantic/economic/deterministic bug
- **Example**: Non-deterministic space ID generation

### Doc/metadata-level

- Bad links, outdated version numbers
- **Example**: Broken links in README.md

## Step 3: Apply Minimal, Compliant Fixes

### For Infrastructure Issues

**Problem**: Missing `v13/scripts/*` files or wrong paths

**Solution**:

```bash
# Copy tools into v13/ tree if Zero-Sim contract requires it
cp scripts/zero_sim_analyzer.py v13/scripts/
cp scripts/zero_sim_autofix.py v13/scripts/

# Or create symlinks
ln -s ../../scripts/zero_sim_analyzer.py v13/scripts/
```

**Rule**: Do NOT modify core logic while fixing scripts.

### For Test Failures (Real Behavior Issues)

**Problem**: Tests fail due to contract violations

**Solution**:

1. Fix the underlying behavior if it violates v1.4 contract:
   - Non-deterministic IDs → Use `DeterministicID.from_string()`
   - Missing EconomicEvents → Add event emission
   - Floating-point use → Convert to `BigNum128`

2. Only update tests when tests were out of sync with agreed semantics

**Example**:

```python
# BAD: Non-deterministic
space_id = str(uuid.uuid4())

# GOOD: Deterministic
from v13.libs.deterministic_helpers import DeterministicID
space_id = DeterministicID.from_string(f"{host}:{timestamp}:{title}")
```

### For Contract/Schema Mismatches

**Problem**: Code and `v13/atlas/contracts.py` out of alignment

**Solution**:

1. Bring code and contracts back into alignment
2. If semantics changed:
   - Update contracts
   - Update docs (`ATLAS_SOCIAL_OVERVIEW.md`, `ATLAS_ECONOMIC_EVENTS.md`, `ZERO_SIM_QFS_ATLAS_CONTRACT.md`)
   - Consider bumping contract version

### For Doc-level Issues

**Problem**: Outdated version numbers, broken links

**Solution**:

```bash
# Update version numbers
sed -i 's/v13.9/v14.0/g' docs/*.md

# Fix broken links
# Update references in documentation
```

**Rule**: Do NOT touch code paths for doc-only fixes.

## Step 4: Re-run Targeted Checks, Then Full CI

### Local Verification

```bash
# 1. Run the specific failing command
python v13/scripts/zero_sim_analyzer.py --dir v13 --exclude legacy_root node_modules --output violation_report.json

# 2. Run affected tests
pytest v13/tests/atlas/test_spaces.py -v

# 3. Run unified social regression
python v13/phase_v14_social_full.py

# 4. Check Zero-Sim compliance
python scripts/zero_sim_analyzer.py --dir v13/atlas --output atlas_violations.json
```

### Push and Verify CI

```bash
# Commit fixes
git add .
git commit -m "fix(ci): <description of fix>"

# Push to feature branch
git push origin feat/atlas-spaces-module

# Monitor CI
# Navigate to: https://github.com/RealDaniG/QFS/actions
```

## Step 5: Maintain Invariants

### DO NOT

❌ Change `BigNum128` or `CertifiedMath` behavior without going through the math regression suite and stewardship rules

❌ Introduce randomness, wall-clock time, floats in economics, or external I/O into consensus/economic/social paths

❌ Let AI/OpenAGI outputs bypass deterministic reward formulas or EconomicEvents

### DO

✅ Use `DeterministicID.from_string()` for all IDs

✅ Use `BigNum128` for all economic calculations

✅ Emit `EconomicEvent` for all social actions

✅ Ensure all timestamps come from external deterministic source (DRV_Packet)

✅ Use `sorted()` for dict/set iterations

## Step 6: Summarize and Document

### Update Task Tracking

Add notes to `task.md`:

```markdown
## CI Fixes Applied

- [x] Fixed missing zero_sim_analyzer.py in v13/scripts/
- [x] Updated workflow to use correct arguments
- [x] Resolved 30 Zero-Sim violations (5 auto-fixed, 25 manual)
```

### Update Walkthrough

Add to walkthrough artifact:

```markdown
### CI Issue: Missing Zero-Sim Files

**Problem**: CI couldn't find `v13/scripts/zero_sim_analyzer.py`
**Solution**: Copied from `scripts/` to `v13/scripts/`
**Verification**: CI now passes Static Analysis step
```

### Update Contracts (if needed)

If changes touch v1.4 guarantees:

1. Update `ZERO_SIM_QFS_ATLAS_CONTRACT.md`
2. Bump version if semantics changed
3. Document in PR description

### PR Description Template

```markdown
## CI Fixes

### Issue 1: [Brief description]
- **Root Cause**: [Explanation]
- **Solution**: [What was changed]
- **Verification**: [How it was tested]

### Issue 2: [Brief description]
- **Root Cause**: [Explanation]
- **Solution**: [What was changed]
- **Verification**: [How it was tested]

## Contract Compliance

- [ ] Zero-Sim v1.4 guarantees maintained
- [ ] No changes to BigNum128/CertifiedMath
- [ ] All social actions emit EconomicEvents
- [ ] Deterministic IDs used throughout
```

## Quick Reference: Common CI Fixes

### Missing Files

```bash
cp scripts/zero_sim_analyzer.py v13/scripts/
git add v13/scripts/zero_sim_analyzer.py
git commit -m "fix(ci): Add zero_sim_analyzer to v13/scripts/"
```

### Wrong Arguments

```yaml
# .github/workflows/ci.yml
- name: Run Zero-Sim Analyzer
  run: |
    python v13/scripts/zero_sim_analyzer.py --dir v13 --exclude legacy_root --output violations.json
```

### Import Errors

```python
# Use absolute imports
from v13.atlas.spaces.spaces_manager import SpacesManager
from v13.libs.BigNum128 import BigNum128
```

### Test Failures

```bash
# Run locally first
pytest v13/tests/atlas/test_spaces.py -xvs

# Fix issues, then verify
pytest v13/tests/atlas/ -v
```

## Automation Checklist

When CI fails, follow this checklist:

- [ ] Identify failing job and extract error message
- [ ] Classify issue (infrastructure/contract/behavior/doc)
- [ ] Apply minimal fix following invariants
- [ ] Run failing command locally
- [ ] Run full test suite locally
- [ ] Commit with descriptive message
- [ ] Push and monitor CI
- [ ] Update task.md and walkthrough
- [ ] Update contracts if semantics changed
- [ ] Document in PR if non-obvious

---

**Last Updated**: 2025-12-18  
**Contract Version**: Zero-Sim v1.4 + ATLAS v14 Social Layer
