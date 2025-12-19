# QFS × ATLAS Documentation Structure Overview

> **Generated:** December 19, 2025  
> **Purpose:** Comprehensive map of all documentation for v15.3 update  
> **Status:** Discovery Complete

## Documentation Categories

### 1. Root Overview & Architecture

| File | Path | Status | Description |
|------|------|--------|-------------|
| README.md | `/README.md` | NEEDS_UPDATE | Main repository overview |
| REPO_STRUCTURE.md | `/REPO_STRUCTURE.md` | NEEDS_UPDATE | Repository structure documentation |
| RELEASE_NOTES_v15.0.0.md | `/RELEASE_NOTES_v15.0.0.md` | OK | v15.0.0 release notes (historical) |
| SECURITY_NOTES.md | `/SECURITY_NOTES.md` | NEEDS_UPDATE | Security documentation |

### 2. Governance & Protocol

| File | Path | Status | Description |
|------|------|--------|-------------|
| HOW_TO_AUDIT_QFS_V15.md | `/HOW_TO_AUDIT_QFS_V15.md` | NEEDS_UPDATE | Auditor guide (needs PoE v15.3) |
| REGRESSION.md | `/REGRESSION.md` | NEEDS_UPDATE | Regression testing documentation |
| POST_AUDIT_PLAN.md | `/POST_AUDIT_PLAN.md` | NEEDS_UPDATE | Post-audit planning |

### 3. Audit & Tests

| File | Path | Status | Description |
|------|------|--------|-------------|
| TEST_INVENTORY.md | `/TEST_INVENTORY.md` | OK | Test inventory (87 files categorized) |
| STAGE_11B_PROGRESS.md | `/STAGE_11B_PROGRESS.md` | OK | Stage 11B completion status |

### 4. PoE & Explain-This

| File | Path | Status | Description |
|------|------|--------|-------------|
| POE_SCHEMA_v1.md | `/docs/POE_SCHEMA_v1.md` | OK | PoE schema v1.0 (just created) |

### 5. Testnet & Operators

| File | Path | Status | Description |
|------|------|--------|-------------|
| TESTNET_STATUS.md | `/TESTNET_STATUS.md` | NEEDS_UPDATE | Testnet status page |
| FIRST_TESTNET_DEPLOYMENT.md | `/FIRST_TESTNET_DEPLOYMENT.md` | NEEDS_UPDATE | Testnet deployment guide |
| NOD_OPERATOR_GUIDE.md | `/NOD_OPERATOR_GUIDE.md` | OK | NOD operator guide (just created) |
| scenarios/README.md | `/scenarios/README.md` | OK | Governance scenarios documentation |

### 6. CI/CD & Verification

| File | Path | Status | Description |
|------|------|--------|-------------|
| VERIFICATION_STATUS.md | `/VERIFICATION_STATUS.md` | OK | Proof-of-safety dashboard (just created) |
| DISCORD_SETUP.md | `/DISCORD_SETUP.md` | OK | Discord integration setup |
| .github/workflows/stage_12_1_pipeline.yml | `/.github/workflows/stage_12_1_pipeline.yml` | OK | Stage 12.1 pipeline |
| .github/workflows/autonomous_verification.yml | `/.github/workflows/autonomous_verification.yml` | OK | Autonomous verification loop |

### 7. Configuration Files

| File | Path | Status | Description |
|------|------|--------|-------------|
| testnet_config.json | `/testnet_config.json` | OK | Testnet configuration |
| testnet_env.template | `/testnet_env.template` | OK | Testnet environment template |

### 8. Legacy/Evidence Files

| File | Path | Status | Description |
|------|------|--------|-------------|
| ROOT_CLEANUP_SUMMARY.md | `/ROOT_CLEANUP_SUMMARY.md` | LEGACY | Historical cleanup summary |
| evidence/phase1/* | `/evidence/phase1/` | LEGACY | Phase 1 evidence (v13.5) |
| v13/evidence/* | `/v13/evidence/` | LEGACY | v13 evidence files |

## Update Priority Order

### Priority 1: Critical User-Facing Docs (IMMEDIATE)

1. **README.md** - Main entry point, must reflect v15.3
2. **HOW_TO_AUDIT_QFS_V15.md** - Auditor guide, needs PoE v15.3 section
3. **TESTNET_STATUS.md** - Public testnet status, needs current info

### Priority 2: Technical Documentation (HIGH)

4. **REPO_STRUCTURE.md** - Repository structure, needs v15.3 updates
5. **SECURITY_NOTES.md** - Security documentation, needs PoE security model
6. **FIRST_TESTNET_DEPLOYMENT.md** - Deployment guide, needs Stage 13 info

### Priority 3: Supporting Documentation (MEDIUM)

7. **REGRESSION.md** - Regression testing, needs current test counts
8. **POST_AUDIT_PLAN.md** - Post-audit planning, needs v15.3 roadmap

### Priority 4: Legacy Cleanup (LOW)

9. Mark legacy files appropriately
10. Add deprecation notices where needed

## Update Checklist

### Facts to Align Across All Docs

- **Version:** v15.3 (PoE Integration)
- **Tests:** 23 tests passing
- **Invariants:** 13 invariants verified
- **Pipeline:** Stage 12.1 (5 quality gates)
- **PoE:** Schema v1.0, automatic generation
- **Testnet:** Stage 13 ready
- **Discord:** Integrated (#📡・bot-status)
- **Verification:** Autonomous (nightly at 02:00 UTC)

### Cross-References to Verify

- All file paths exist
- All commands are executable
- All version numbers consistent
- All test/invariant counts match

### New Content to Add

- PoE v15.3 references
- Stage 12.1 pipeline mentions
- Stage 13 testnet readiness
- Discord notification info
- Autonomous verification details
- Replay tool references

## Status Summary

**Total Documentation Files:** 117 (md, rst, txt)  
**Configuration Files:** 65 (json, yml, yaml)  
**Workflow Files:** 6 (GitHub Actions)

**Status Breakdown:**

- ✅ **OK (Up-to-date):** 8 files
- ⚠️ **NEEDS_UPDATE:** 8 files (Priority 1-3)
- 📦 **LEGACY:** ~100 files (evidence, logs, historical)

**Next Steps:**

1. Update Priority 1 files (README, audit guide, testnet status)
2. Update Priority 2 files (structure, security, deployment)
3. Update Priority 3 files (regression, post-audit)
4. Mark legacy files appropriately

---

**Documentation update will ensure all docs reflect v15.3 reality: structural verifiability, PoE integration, testnet readiness.**
