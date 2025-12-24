# QFS × ATLAS — Developer Bounties 💰

Welcome to the **QFS × ATLAS Developer Bounty Program**! Help us build the future of quantum-resistant autonomous finance.

> **Status**: ACTIVE 🟢
> **Focus**: GitHub Identity, Retroactive Rewards, and Zero-Sim Hardening.

---

## 🛠️ GitHub Identity & Retroactive Rewards

We are integrating GitHub identity to enable **provable, retroactive rewards** for contributors. This system relies on a **Zero-Sim** architecture where:

1. **Identity is an Event**: Linking a wallet to GitHub emits an immutable `identity_link.github` event.
2. **Contributions are Deterministic**: We import GitHub data using a strictly deterministic ledger format (Phase 2).
3. **Rewards are Pure**: logic in the F-Layer computes rewards from EvidenceBus events only (Phase 4).

---

## 🚀 Available Bounties

| ID | Title | Reward | Difficulty | Status |
|----|-------|--------|------------|--------|
| **BNT-GITHUB-01** | **Wallet ↔ GitHub Identity Link**<br>Implement `/auth/bind-github` to emit `identity_link.github` events. | **600 CHR** | Hard 🌶️🌶️🌶️ | **COMPLETED** |
| **BNT-GITHUB-IMPORT-01** | **Deterministic GitHub Importer**<br>Build `tools/github_import_contributions.py` to produce replayable contribution ledgers. | **500 CHR** | Medium 🌶️🌶️ | **COMPLETED** |
| **BNT-GITHUB-IMPORT-02** | **Contribution Ingestion**<br>Implement `/api/bounties/import-contrib` to ingest ledgers as `contrib_recorded` PoE events. | **600 CHR** | Hard 🌶️🌶️🌶️ | **COMPLETED** |
| **BNT-RETRO-REWARDS-01** | **Retroactive Reward Simulation**<br>Implement F-Layer logic to compute reward allocations from PoE events deterministically. | **800 CHR** | Hard 🌶️🌶️🌶️ | **COMPLETED** |
| **BNT-BOUNTY-EXPLORER-UI** | **ATLAS Bounty Explorer**<br>Build UI to view rounds, allocations, and link to PoE proofs. | **700 CHR** | Hard 🌶️🌶️🌶️ | **COMPLETED** |
| **BNT-MOCKQPC-01** | **MOCKQPC Verification Infrastructure**<br>Implement verification tools for batched PoE signatures. | **800 CHR** | Hard 🌶️🌶️🌶️ | **OPEN** |
| **BNT-COST-01** | **Cost-Efficiency Audit Tool**<br>CLI tool to track PQC calls and infrastructure costs. | **400 CHR** | Medium 🌶️🌶️ | **OPEN** |

### Maintenance / Hardening (Previously v16/v17)

| ID | Title | Status |
|----|-------|--------|
| **BNT-20251218-01** | Implementation of Living Posts (Phase 1) | **COMPLETED** |
| **BNT-20251218-02** | CI/CD Pipeline Enhancement | **COMPLETED** |
| **BNT-20251218-03** | Expand Unit Test Coverage | **COMPLETED** |
| **BNT-20251218-04** | Type Safety Hardening (v13/libs) | **COMPLETED** |
| **BNT-20251218-05** | Documentation Gap Analysis | **COMPLETED** |

---

## ✅ Verification & Acceptance

All bounties must pass the **Zero-Sim Verification** suite.

1. **System Health**:

    ```powershell
    ./run_atlas_full.ps1
    # Must return Exit Code 0
    ```

2. **Zero-Sim Compliance**:

    ```bash
    python scripts/check_zero_sim.py
    # Must report SUCCESS: No Zero-Sim violations found.
    ```

3. **Determinism & Replay**:
    * **GitHub Import**: `tools/github_import_contributions.py` must produce identical JSON ledgers for the same input parameters.
    * **PoE Replay**: Replaying `identity_link.github` and `contrib_recorded` events must result in identical state projections.

---

## 📝 Bounty Template

When submitting a Pull Request for a bounty, please copy the template below into your PR description.

```markdown
### 🎯 Bounty Submission

**Bounty ID**: BNT-XXXX-XX
**Title**: [Bounty Title]

### 🛠️ Implementation Details
- [Brief description of changes]
- [List of files modified]

### ✅ Verification
- [ ] System Health: `./run_atlas_full.ps1` (Pass)
- [ ] Zero-Sim: `python scripts/check_zero_sim.py` (Pass)
- [ ] Determinism Verified (for GitHub/Rewards)

### 👤 Contributor Info
- **Wallet ID (for payout)**: [Your Testnet Wallet Address]
```

## 📜 Rules & Guidelines

1. **EvidenceBus First**: Every cross-system action exists only as an event.
2. **Quality Code**: `mypy` compliant, PEP8.
3. **Zero Regression**: Must not break existing v14/v18 baselines.
4. **Tests Required**: Unit tests for all new logic.

See [The Contributor Journey in CONTRIBUTING.md](CONTRIBUTING.md) for full setup instructions.
