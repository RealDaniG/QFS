# QFS × ATLAS: Quantum Financial System

> **Latest Release:** [v15.0.0 - Autonomous Governance](RELEASE_NOTES_v15.0.0.md) 🎉  
> **Status:** Production-Ready - Testnet Deployment  
> **Test Coverage:** 23/23 tests passing, 13/13 invariants verified

## 🚀 v15.0.0 Highlights

- **Autonomous Governance:** Self-amending protocol with deterministic proposal execution
- **100% Test Coverage:** All governance-critical and operational behaviors verified
- **Deterministic Replay:** Zero drift, bit-for-bit reproducibility
- **AEGIS Coherence:** Cross-layer verification ensuring system integrity
- **Ready for Testnet:** Complete audit trail, external review package prepared

[📖 Read Full Release Notes](RELEASE_NOTES_v15.0.0.md) | [🧪 Quick Start Guide](#quick-start)

---

# Quantum Financial System (QFS) V14.0 – Deterministic Session Management

> **A deterministic, post‑quantum economic engine for decentralized social media, with constitutional guards and cryptographic, replayable auditability.**

---

## 🎯 Quick Start

| I want to... | Go here |
|--------------|---------|
| **Understand the system** | [Core Concepts](v13/docs/QFS_V13_8_FULL_ENGINE_OVERVIEW.md) · [📖 Wiki](https://github.com/RealDaniG/QFS/wiki) |
| **Deploy to production** | [Production Deployment](v13/docs/OPERATOR_RUNBOOK_V13.8.md) |
| **Review security** | [Security Compliance](v13/docs/ZERO_SIM_QFS_ATLAS_CONTRACT.md) |
| **Contribute** | [Contributing](v13/docs/roadmaps/TASKS-V13.5.md) |
| **Check status** | [Interactive Dashboard](v13/docs/qfs-v13.8-dashboard.html) |
| **Browse documentation** | [📚 Full Wiki](v13/docs/README.md) |

---

## 📊 Current Status

### V14.0 "Deterministic Session Management" (RELEASED) ✅ LIVE

This release delivers the complete deterministic session management system with challenge-response authentication, ledger-replayable state reconstruction, and Explain-This cryptographic proof integration. It also marks the activation of the **Autonomous Validation Framework**.

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| Constitutional Guards | ✅ Deployed | 937 lines | 100% |
| **Autonomous Validation**| ✅ Live | Phase 0/2 | 100% |
| Zero-Sim Compliance | ✅ Verified | 0 violations | Production |
| **PQC Provider** | ✅ Integrated | Mock/Real | 100% |
| **Observability** | ✅ Verified | Trace Analysis | End-to-End |
| Pipeline Compliance | ✅ Verified | 0 violations | Production |
| AEGIS Integration | ✅ Verified | Test service ready | Staged |
| Explanation Audit | ✅ Ready | Backend + UI | Complete |
| Full-Stack Determinism | ✅ PASS | Nightly E2E green | Verified |
| **Trust Loop** | ✅ Verified | v13/scripts/L-001 | Passed |
| **Session Management** | ✅ RELEASED | Deterministic | 100% |

**Release Date:** 2025‑12-19
**Constitutional Status:** Guards enforced at all economic and governance gates
**Performance Target:** 2,000 TPS with full guard stack under AEGIS‑verified nodes

📈 [View Real-Time Dashboard](v13/docs/qfs-v13.8-dashboard.html) | 📋 [Full Compliance Report](QFS_V13_FULL_COMPLIANCE_AUDIT_REPORT.json)

---

## 🤝 Contributing & Bounties

![Bounties Available](https://img.shields.io/badge/bounties-5-brightgreen) ![Total Rewards](https://img.shields.io/badge/rewards-1400_CHR-blue)

We welcome community contributions through our **Developer Rewards Program**. Check out:

- **[BOUNTIES.md](BOUNTIES.md)**: View active paid tasks.
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Setup guide and coding standards.

### Quick Start

```bash
git clone https://github.com/your-org/qfs-atlas.git && cd qfs-atlas
python -m venv venv && venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
pre-commit install
pytest v13/tests/
```

## 🏗️ Architecture Overview

QFS V14.0 runs beneath the ATLAS social layer as a zero‑simulation, multi‑token economic engine with explainable rewards, PQC‑secured consensus, and decentralized storage.

```

┌─────────────────────────────────────────────────────────┐
│                 ATLAS Social Platform                   │
│          (Censorship-Resistant P2P/TOR Network)         │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   QFS V14.0 Engine                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Constitutional│  │  Zero-Sim    │  │ ExplainThis  │  │
│  │    Guards    │  │    Replay    │  │    Audit     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   6-Token    │  │    AEGIS     │  │     PQC      │  │
│  │  Economics   │  │Verification  │  │ Signatures   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐                                     │
│  │   Sessions   │                                     │
│  │  Management  │                                     │
│  └──────────────┘                                     │
└─────────────────────────────────────────────────────────┘

```

---

## 📱 ATLAS Frontend

ATLAS is the user-facing web application that provides wallet-based authentication, encrypted chat, and social features powered by the QFS economic engine.

**ATLAS Documentation:** [v13/ATLAS/README.md](v13/ATLAS/README.md)

**Key Features:**

- Wallet-based identity
- End-to-end encrypted messaging
- Referral system with Genesis Points
- Real-time coherence scoring
- Deterministic session management with challenge-response authentication

---

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

📖 **Token Documentation:** [Wiki: Six-Token Economics](https://github.com/RealDaniG/QFS/wiki) _(Coming soon: Full NOD spec)_

---

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

### Phase 3 Auditing & Observability

- **Structured Logging**: All operations now emit JSON structured logs with `TraceContext` propagation.
- **Consistency Proofs**: `CertifiedMath` logs are cryptographically bound to the audit trail via `pqc_cid`.
- **PQC Abstraction**: OS-agnostic `IPQCProvider` ensures deterministic crypto operations across dev/prod environments.
- **Session Management**: Deterministic session layer with challenge-response authentication and ledger replay.

🔐 [Guard Implementation](v13/guards)

### Recent Security Fixes (PR #5)

**🔴 Critical Issues Resolved:**

- ✅ Added authentication to all `/explain/*` endpoints
- ✅ Replaced hardcoded `localhost` URLs with environment-aware API base
- ✅ Removed side-effectful `__main__` blocks from production modules (Phase 14 Remediation)
- ✅ Implemented secure logging (redacted topology, hashed sensitive IDs)

📋 [Security Remediation Details](https://github.com/RealDaniG/QFS/pull/5)

---

## 🚀 Production Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (cache only, non-authoritative)
- Ubuntu 22.04+ (for PQC production)
- Docker (optional)

### Installation

```

# Clone repository

git clone <https://github.com/RealDaniG/QFS.git>
cd QFS/v13

# Install dependencies

pip install -r requirements.txt

# Verify Zero-Sim compliance

python scripts/zero-sim-ast.py

# Run core tests

python -m pytest tests/ -v

```

### Environment Configuration

```

# .env.production

EXPLAIN_THIS_SOURCE=qfs_ledger  # NO MOCKS in production
QFS_API_URL=<https://api.qfs.example.com>  # HTTPS only
AEGIS_API_URL=<https://aegis.qfs.example.com>
NEXT_PUBLIC_API_URL=/api
SESSION_CHALLENGE_TTL=3600  # Session challenge TTL in seconds

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
- [ ] Session management system tested and verified

📖 [Operator Runbook (Production)](v13/docs/OPERATOR_RUNBOOK_V13.8.md)

---

## 🧪 Testing & Verification

### Test Suites

```

# Core determinism

python -m pytest v13/tests/test_full_stack_determinism.py -v

# Humor signal slice (47 tests)

python -m pytest v13/tests/test_humor_*.py -v

# Value-node replay (28 tests)

python -m pytest v13/tests/test_value_node_*.py -v

# Session management (17 tests)

python -m pytest v13/tests/sessions/ -v

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
- `sessions/` – Session management test evidence
- `nightly/` – Nightly E2E results

🔍 [Browse Evidence](v13/evidence)

---

## 📚 Documentation

### For Users

- [ATLAS Web UI Guide](v13/ATLAS/README.md) – Frontend user interface
- [Explain-This System](v13/docs/EXPLANATION_AUDIT_SPEC.md) – Reward transparency
- [Humor Signal Overview](v13/docs/QFS_V13_7_HUMOR_SIGNAL_ADDON.md) – 7-dimensional comedy rewards
- [Session Management System](v13/docs/SESSION_MANAGEMENT_SYSTEM.md) – Deterministic session layer
- [📖 **Full Wiki**](https://github.com/RealDaniG/QFS/wiki) – Complete documentation hub

### For Developers

- [Zero-Sim Contract v1.3](v13/docs/ZERO_SIM_QFS_ATLAS_CONTRACT.md) – **Start here**
- [StorageEngine Spec](v13/docs/STORAGEENGINE_INTERFACE_SPEC.md) – Decentralized storage
- [Session Management System](v13/docs/SESSION_MANAGEMENT_SYSTEM.md) – Deterministic session layer with challenge-response authentication
- [📖 **Developer Wiki**](https://github.com/RealDaniG/QFS/wiki) – API docs, architecture guides

### For Auditors

- [Full Compliance Report](QFS_V13_FULL_COMPLIANCE_AUDIT_REPORT.json) – 89 requirements
- [Security Audit (PR #5)](https://github.com/RealDaniG/QFS/pull/5) – Recent security fixes
- [Evidence Index](v13/docs/roadmaps/ROADMAP-V13.5-REMEDIATION.md#evidence-index) – All verification artifacts

---

## 🤝 Contributing

### Current Focus:# QFS v19.0 × ATLAS v1.3 (v15 Autonomous Governance LIVE)
>
> **Status:** Stage 7 Release Complete. v15 Autonomous Governance Active.

QFS is a quantum-secure, constitutionally deterministic financial operating system.

## 🚀 Latest Developments (v15)

**Stage 7 Autonomous Governance** is now LIVE.

- **Self-Amendment**: Hash-bound proposals update economic parameters via `v15/atlas/governance`.
- **Proof-of-Execution**: Every governance action generates a verifiable artifact.
- **Tezos-Inspired**: Phased Proposal → Vote → Execute cycle.
- [Read the Release Notes](docs/RELEASES/RELEASE_NOTES_v15_0_0.md) or [v15 Overview](docs/V15_OVERVIEW.md).

2. Challenge-response authentication flow
3. Ledger-replayable session state reconstruction
4. Explain-This cryptographic proof integration

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

---

## 📈 Roadmap

### Completed Phases

- ✅ **Phase 0** (Days 1-7): Baseline verification
- ✅ **Phase 1** (Days 8-60): Core determinism (80% → 100%)
- ✅ **V13.6**: Constitutional guards deployed
- ✅ **V13.8**: Zero-Sim Absolute / Pipeline Compliance (Phase 14)
- ✅ **Session Management System**: Deterministic session layer with challenge-response authentication
- ✅ **V14.0**: Full session management system release with Autonomous Validation Framework

### Current Phase

🔵 **Phase 2.5: Trust Loop Validation** (Active)

- ✅ Minimal Trust Loop (Wallet -> Chat -> Referrals -> Reward)
- ✅ Batch Event API
- ✅ Deterministic User Identifiers
- ✅ Session Management System

🔵 **ATLAS v1.3 "Governance Live"** (Q1 2026)

- Deploy production AEGIS service
- Launch governance voting portal
- Public audit dashboard with hash verification

### Future Phases

- **Phase 2**: HSM/KMS integration, SBOM, reproducible builds
- **Phase 3**: Threat modeling, oracle framework, multi-node replication
- **Phase 4**: Fuzzing, static analysis, governance procedures
- **Phase 5** (Days 301-365): Final certification, 100% compliance

📅 [Full Roadmap](v13/docs/roadmaps/ROADMAP-V13.5-REMEDIATION.md)

---

## 🏆 Key Achievements

- **Zero-Mock Verified:** 0 violations in production code
- **Full-Stack Determinism:** Bit-exact replay across entire stack
- **Constitutional Guards:** 3-layer enforcement (economics, NOD, AEGIS)
- **Trust Loop Verified:** End-to-end validation of social-economic cycle
- **Secure Chat V2:** PQC-ready, E2E encrypted messaging with sequence enforcement
- **Referral System:** Ledger-backed, deterministic invitation logic
- **Explain-This Framework:** Cryptographically auditable reward transparency
- **PQC Ready:** CRYSTALS-Dilithium signatures on all ledger writes
- **Session Management System:** Deterministic, replayable session layer with challenge-response authentication and Explain-This integration

---
