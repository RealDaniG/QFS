# QFS V13 — Full Project Changelog

All notable changes to QFS V13 will be documented here.

This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [13.8.0] — 2025-12-14

### QFS V13.8 – Explain-This & Value Node Integration (ATLAS 1.1)

**Release Theme:** Transparency, Replayability, and User-Facing Explainability.

**Core Transition:**

- V13.6 = Constitutional & Operational Safety
- V13.8 = User-Visible Determinism & Explanaibility

#### Added

**Value-Node Replay Engine (V13.8)**

- Implemented `ValueNodeReplayEngine` (`v13/policy/value_node_replay.py`)
- Reconstructs user value state deterministically from `ValueGraphRef` and ledger events.
- Generates **SHA-256 hash** for every reconstructed state.
- Supports generic event replay: `RewardAllocated`, `InteractionCreated`, `ContentCreated`.

**Explain-This APIs (ATLAS 1.1)**

- `GET /explain/reward/{wallet_id}`: Returns breakdown of Base Reward, Bonuses, Caps, and Guard Actions.
- `GET /explain/ranking/{content_id}`: Returns breakdown of Visibility Score, Interaction Volume, Quality Base, and Neighbor Context.
- Fully wired to Replay Engine for zero-simulation compliance.

**Hardened Signal System (Humor)**

- Integrated `HumorSignalAddon` as a reference implementation for governed signals.
- Pure signal logic (no direct economic mutation).
- Deterministic output verification.

**Frontend Integration (ATLAS 1.1)**

- `ExplainThisPanel.tsx`: Unified React component for visualizing reward and ranking logic.
- `useExplain.ts`: Hook for fetching verified explanations from API.
- Deep integration into `WalletInterface` (Transaction History) and `DiscoveryInterface` (Trending Topics).

#### Changed

**Documentation**

- **ATLAS README**: Completely rewritten to reflect the "Deterministic, Two-Sided Explain-This Platform" vision.
- **Root README**: Updated to reflect V13.8 status and link to ATLAS 1.1 specs.
- **Roadmap**: Marked all Explain-This tasks as `COMPLETED`.

#### Verified

- **End-to-End Determinism**: Verified via `tests/test_explain_this_e2e.py` (Hash: `a23a72a9...`).
- **Zero-Simulation Compliance**: Verified via static analysis and replay tests.

---

## [13.6.0] — 2025-12-13

### QFS V13.6 – Constitutional Integration Release

(See `CHANGELOG_V13.6.md` for full details)
