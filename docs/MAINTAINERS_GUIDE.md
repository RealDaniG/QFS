# QFS × ATLAS Maintainer Guide

> **Status:** Evergreen v16 Baseline  
> **Role:** Operational Security & Governance

---

## 🛡️ Branch Protection Rules

To maintain the **v16 Baseline** and **Zero-Sim** integrity, the `main` and `develop` branches MUST be protected with the following settings in GitHub:

### 1. Require Status Checks to Pass

**Strictly Required:**

- `static-analysis` (Zero-Sim, Pylint, Bandit)
- `mockqpc-compliance` (Zero-Sim + MOCKQPC determinism)
- `autonomous-validation` (Constitutional check)
- `unit-tests` (Core logic coverage)
- `determinism-fuzzer` (Replay verification)

**Rationale:** Breaking any of these breaks the "Zero-Sim" contract ($0 cost, 100% determinism).

### 2. Require Pull Request Reviews

**Minimum:** 1 approval.
**Codeowners:** Enable "Require review from Code Owners".

**Critical Paths:**

- `current baseline/crypto/*` → Requires Security Expert review.
- `current baseline/governance/*` → Requires Governance Council review.
- `evidence_bus.py` → Requires Core Maintainer review.

---

## 🔍 Triage & Labeling

Use labels to categorize capabilities and invariant risks.

| Label | Meaning |
| :--- | :--- |
| `type:determinism` | Modifies sort order, math, or logic flow. Needs Replay Test. |
| `type:cost` | Affects PQC frequency or Agent sampling. Needs Cost Audit. |
| `area:governance` | Changes rules, voting, or treasury. |
| `area:evidencebus` | Changes log schema or emitters. |
| `area:mockqpc` | Changes crypto adapters or stubs. |
| `area:wallet-auth` | Changes authentication adapters or session logic. |

## 🔑 Authentication Implementation (v16)

All authentication MUST follow the **EvidenceBus-Centric** pattern:

1. **Frontend**: Signs SHA256(message) via EIP-191.
2. **Adapter**: Verifies signature (MOCKQPC or Real).
3. **SessionManager**: Creates session AND emits `AUTH_LOGIN` event to EvidenceBus.
4. **Zero-Sim**: No database writes for sessions; use in-memory or deterministic cache.

---

## 🚨 Security Incident Response

If a vulnerability or non-deterministic leak is found:

1. **Freeze**: Pause all merges to `main`.
2. **Isolate**: Identify if it's a "Logic" bug (revert code) or "State" bug (requires replay patch).
3. **Fix**: Apply patch via `hotfix/` branch.
4. **Verify**: Run `scripts/verify_determinism.py --runs 1000`.
5. **Release**: Tag new patch version.

---

## 📈 Release Workflow

1. **Cut Branch**: `release/vX.Y.Z` from `develop`.
2. **Audit**: Run full regression suite + MOCKQPC verifier.
3. **Tag**: Signed git tag `vX.Y.Z`.
4. **Deploy**:
    - **Dev/Beta**: Auto-deploy via CI to single-node.
    - **Mainnet**: Governance proposal required for consensus upgrades.
