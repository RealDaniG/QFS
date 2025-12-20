# QFS × ATLAS — Release Notes

> **Current Version:** v17.0.0-beta-governance-bounties
> **Theme:** Deterministic Governance, Bounties, Social Surface, and Agent Advisory (Layer D)
> **Status:** Full Feature Complete (Beta)

---

## 🚀 v17.0.0-beta (December 20, 2025)

**Major Milestone**: "Compression and Reveal". The core F-Layer engine is now fully deterministic and surfaced via human-readable UI projections.

### New Features

#### 1. Governance F-Layer (`v17/governance`)

- Deterministic Proposal Creation, Voting, and Execution.
- Quorum rules, Approval thresholds, and Tie-breaking logic.
- Full PoE logging to EvidenceBus.

#### 2. Bounty F-Layer (`v17/bounties`)

- Creation, Contribution Tracking, and Reward Allocation.
- Configurable reward caps and algorithms.

#### 3. Social Surface (`v17/social`)

- Threads bound to Governance/Bounties.
- Dispute lifecycle management.
- User Profiles with contribution history.

#### 4. Layer D Advisory (`v17/agents`)

- Non-authoritative agent signals overlaid on UI.
- Heuristics for:
  - **Governance**: High amounts, short descriptions, spam.
  - **Bounties**: Reference links, content quality.
  - **Social**: Urgency keywords ("scam", "fraud").

### Verification

- **Zero-Sim**: 100% Deterministic execution enforced by CI.
- **Replay**: Full state reconstruction from EvidenceBus.

---

## 📜 v16.1.0 (Previous Stable)

**Theme**: Foundations (Auth, Admin, PoE)

- **Authentication**: EIP-191 Wallet Signatures + Session Management.
- **Admin Dashboard**: Evidence Chain Viewer.
- **Infrastructure**: EvidenceBus v1, MOCKQPC v1.

## 🕰️ v15.5 (Legacy)

- Initial PoE prototypes.
- Cost-efficient architecture basics.
