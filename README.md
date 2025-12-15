# Quantum Financial System (QFS) V13.8 – Zero‑Sim Absolute

> **A deterministic, post‑quantum economic engine for decentralized social media, with constitutional guards and cryptographic, replayable auditability.**

***

## 🎯 Quick Start

| I want to... | Go here |
|--------------|---------|
| **Understand the system** | [Core Concepts](#core-concepts) |
| **Deploy to production** | [Production Deployment](#production-deployment) |
| **Review security** | [Security Compliance](#security-compliance) |
| **Contribute** | [Contributing](#contributing) |
| **Check status** | [Interactive Dashboard](docs/qfs-v13.8-dashboard.html) |

***

## 📊 Current Status

### V13.8 “Zero‑Sim Absolute” ✅ COMPLETE

This release locks the full stack into audited, replayable determinism: every ledger write is PQC‑signed, every reward and ranking is explainable via zero‑simulation replay, and all constitutional guards are wired into the production pipeline.

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| Constitutional Guards | ✅ Deployed | 937 lines | 100% |
| Zero-Mock Compliance | ✅ Verified | 0 violations | Production |
| Pipeline Compliance | ✅ Verified | 0 violations | Production |
| AEGIS Integration | 🟡 Staged | Test service ready | Prod pending |
| Explanation Audit | ✅ Ready | Backend + UI | Complete |
| Full-Stack Determinism | ✅ PASS | Nightly E2E green | Verified |

**Release Date:** 2025‑12‑15  
**Constitutional Status:** Guards enforced at all economic and governance gates  
**Performance Target:** 2,000 TPS with full guard stack under AEGIS‑verified nodes

📈 [View Real-Time Dashboard](docs/qfs-v13.8-dashboard.html) | 📋 [Full Compliance Report](QFS_V13_FULL_COMPLIANCE_AUDIT_REPORT.json)

***

## 🏗️ Architecture Overview

QFS V13.8 runs beneath the ATLAS social layer as a zero‑simulation, multi‑token economic engine with explainable rewards, PQC‑secured consensus, and decentralized storage.

```
┌─────────────────────────────────────────────────────────┐
│                    ATLAS Social Platform                 │
│            (Censorship-Resistant P2P/TOR Network)       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   QFS V13.8 Engine                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Constitutional│  │   Zero-Sim   │  │ ExplainThis  │  │
│  │    Guards     │  │    Replay    │  │    Audit     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  6-Token      │  │    AEGIS     │  │     PQC      │  │
│  │  Economics    │  │  Verification│  │   Signatures │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

***

## 🎓 Core Concepts

### What is QFS?

QFS is a **deterministic economic engine** that:

1. **Never lies** – Every balance, reward, and rank is reproducible by ledger replay.  
2. **Never drifts** – Same inputs → same outputs, across nodes and over time.  
3. **Never hides** – All decisions emit hash‑verifiable evidence from day one.  
4. **Never centralizes** – AEGIS‑gated node set and NOD‑scoped governance.  
5. **Never breaks security** – PQC‑signed ledger writes, fail‑closed invariants.

### Six‑Token Economic System

QFS models the network with six orthogonal tokens: five user‑visible assets and one infrastructure‑only governance token.

| Token | Symbol | Purpose | Transferable |
|-------|--------|---------|--------------|
| Coherence | CHR | System stability and baseline incentives | ✅ Yes |
| Flexibility | FLX | User rewards, penalties, and elastic incentives | ✅ Yes |
| Psi‑Sync | SYNC | Predictive alignment and coordination | ✅ Yes |
| Attestation | ATR | Reputation, proofs, and evidence of behavior | ✅ Yes |
| Reserve | RES | Safety buffer and macro‑stability | ✅ Yes |
| **Node Operator** | **NOD** | **Infrastructure‑only governance by operators** | ❌ **No** |

> **🔒 Critical:** NOD is non‑transferable and firewalled from user‑facing parameters; it can shape infrastructure, never individual outcomes.

📖 [Full Token Specification](docs/qfs_v13_plans/NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md)

***

## 🛡️ Security Compliance

### Zero-Simulation Contract v1.3

QFS enforces **mathematical determinism** across all layers:

- ✅ **No Randomness** – Deterministic PRNG only, seeded by content hash
- ✅ **No Wall-Clock Time** – Ledger timestamps only (tick-based)
- ✅ **No Floating-Point Economics** – BigNum128 integer-scaled arithmetic
- ✅ **No External I/O in Consensus** – Pure functions, in-memory only
- ✅ **PQC Signatures Required** – CRYSTALS-Dilithium on all ledger writes

📜 [Read Full Contract](v13/docs/ZERO_SIM_QFS_ATLAS_CONTRACT.md)

### Constitutional Guards

Three layers of enforcement:

1. **EconomicsGuard** (937 lines) – Validates CHR/FLX/RES rewards against constitutional bounds
2. **NODInvariantChecker** (682 lines) – Enforces non-transferability, supply conservation, voting limits
3. **AEGISNodeVerification** (733 lines) – Pure deterministic node verification with PQC identity

🔐 [Guard Implementation](v13/guards)

### Recent Security Fixes (PR #5)

**🔴 Critical Issues Resolved:**

- ✅ Added authentication to all `/explain/*` endpoints
- ✅ Replaced hardcoded `localhost` URLs with environment-aware API base
- ✅ Removed side-effectful `__main__` blocks from production modules (Phase 14 Remediation)
- ✅ Implemented secure logging (redacted topology, hashed sensitive IDs)

📋 [Security Remediation Details](https://github.com/RealDaniG/QFS/pull/5)

***

## 🚀 Production Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (cache only, non-authoritative)
- Ubuntu 22.04+ (for PQC production)
- Docker (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/RealDaniG/QFS.git
cd QFS/v13

# Install dependencies
pip install -r requirements.txt

# Verify Zero-Sim compliance
python scripts/zero-sim-ast.py

# Run core tests
python -m pytest tests/ -v
```

### Environment Configuration

```bash
# .env.production
EXPLAIN_THIS_SOURCE=qfs_ledger  # NO MOCKS in production
QFS_API_URL=https://api.qfs.example.com  # HTTPS only
AEGIS_API_URL=https://aegis.qfs.example.com
NEXT_PUBLIC_API_URL=/api
```

### Deployment Checklist

- [ ] All tests passing (`pytest v13/tests -q`)
- [ ] Zero-Mock scanner clean (`python scripts/scan_zero_mock_compliance.py`)
- [ ] HTTPS-only enforced (HSTS headers)
- [ ] Authentication wired to `/explain/*` endpoints
- [ ] Rate limiting enabled (prevent enumeration)
- [ ] PQC signatures verified on all ledger writes
- [ ] AEGIS production service deployed
- [ ] Nightly E2E pipeline green

📖 [Operator Runbook (Production)](v13/docs/OPERATOR_RUNBOOK_V13.8.md)

***

## 🧪 Testing & Verification

### Test Suites

```bash
# Core determinism
python -m pytest v13/tests/test_full_stack_determinism.py -v

# Humor signal slice (47 tests)
python -m pytest v13/tests/test_humor_*.py -v

# Value-node replay (28 tests)
python -m pytest v13/tests/test_value_node_*.py -v

# ATLAS API boundaries
python -m pytest v13/ATLAS/src/tests -v

# Nightly E2E
python scripts/generate_full_stack_evidence.py
```

### Evidence Artifacts

All verification evidence is in `v13/evidence/`:

- `zero_sim/` – Full-stack determinism proofs
- `humor/` – Humor signal compliance bundle
- `value_node/` – Value-node replay evidence
- `storage/` – StorageEngine replay status
- `nightly/` – Nightly E2E results

🔍 [Browse Evidence](v13/evidence)

***

## 📚 Documentation

### For Users

- [ATLAS Web UI Guide](v13/ATLAS/README.md) – Frontend user interface
- [Explain-This System](v13/docs/EXPLANATION_AUDIT_SPEC.md) – Reward transparency
- [Humor Signal Overview](v13/docs/QFS_V13_7_HUMOR_SIGNAL_ADDON.md) – 7-dimensional comedy rewards

### For Developers

- [Zero-Sim Contract v1.3](v13/docs/ZERO_SIM_QFS_ATLAS_CONTRACT.md) – **Start here**
- [API Reference](v13/ATLAS/src/api/README.md) – REST endpoints
- [StorageEngine Spec](v13/docs/STORAGEENGINE_INTERFACE_SPEC.md) – Decentralized storage
- [Value Node Replay](v13/docs/QFS_V13_VALUE_NODE_EXPLAINABILITY.md) – Economic views

### For Auditors

- [Full Compliance Report](QFS_V13_FULL_COMPLIANCE_AUDIT_REPORT.json) – 89 requirements
- [Security Audit (PR #5)](https://github.com/RealDaniG/QFS/pull/5) – Recent security fixes
- [Evidence Index](v13/docs/roadmaps/ROADMAP-V13.5-REMEDIATION.md#evidence-index) – All verification artifacts

***

## 🤝 Contributing

### Current Focus: ATLAS v1.3 "Governance Live"

We're moving from verified baseline → live production with:

1. Real AEGIS DID verification service
2. Governance voting portal
3. Public audit dashboard

📋 [View Open Tasks](v13/docs/roadmaps/TASKS-V13.5.md)

### How to Contribute

1. **Understand current state**  
   Read [`QFS_V13_FULL_COMPLIANCE_AUDIT_REPORT.json`](QFS_V13_FULL_COMPLIANCE_AUDIT_REPORT.json)

2. **Pick a task**  
   Check [`TASKS-V13.5.md`](v13/docs/roadmaps/TASKS-V13.5.md) for current priorities

3. **Follow evidence-first principle**  
   All work must generate evidence artifacts in `v13/evidence/`

4. **Maintain Zero-Sim compliance**  
   - No floats, random, or time-based operations  
   - All math via BigNum128 or CertifiedMath  
   - PQC signatures for critical ops  
   - SHA3-512 for all hashing  

5. **Submit PR**  
   Reference specific task ID (e.g., P1-T001), include evidence, update docs

***

## 📈 Roadmap

### Completed Phases

- ✅ **Phase 0** (Days 1-7): Baseline verification
- ✅ **Phase 1** (Days 8-60): Core determinism (80% → 100%)
- ✅ **V13.6**: Constitutional guards deployed
- ✅ **V13.8**: Zero-Sim Absolute / Pipeline Compliance (Phase 14)

### Current Phase

🔵 **ATLAS v1.3 "Governance Live"** (Q1 2026)

- Deploy production AEGIS service
- Launch governance voting portal
- Public audit dashboard with hash verification

### Future Phases

- **Phase 2** : HSM/KMS integration, SBOM, reproducible builds
- **Phase 3** Threat modeling, oracle framework, multi-node replication
- **Phase 4** : Fuzzing, static analysis, governance procedures
- **Phase 5** (Days 301-365): Final certification, 100% compliance

📅 [Full Roadmap](v13/docs/roadmaps/ROADMAP-V13.5-REMEDIATION.md)

***

## 🏆 Key Achievements

- **Zero-Mock Verified:** 0 violations in production code
- **Full-Stack Determinism:** Bit-exact replay across entire stack
- **Constitutional Guards:** 3-layer enforcement (economics, NOD, AEGIS)
- **Explain-This Framework:** Cryptographically auditable reward transparency
- **PQC Ready:** CRYSTALS-Dilithium signatures on all ledger writes
- **47 Humor Tests:** 100% Zero-Sim compliant signal slice
- **28 Value-Node Tests:** Deterministic replay + explainability

***

## 📞 Support & Community

- **Issues:** [GitHub Issues](https://github.com/RealDaniG/QFS/issues)
- **Discussions:** [GitHub Discussions](https://github.com/RealDaniG/QFS/discussions)
