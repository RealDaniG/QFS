> ⚠️ Historical Document (Archived)
> This file describes QFS V13.5 / V13.7 / V13.8 behavior and is **not** representative of the current Phase IV/V implementation.
> For up-to-date information, see `v13/docs/phase4_walkthrough.md`, `task.md`, and `docs/EXECUTIVE_SUMMARY.md`.

# QFS V13.8 – Full Engine Overview (Post‑V13.5 Updates)

QFS V13.x is now a fully structured, Zero‑Sim–compliant, ATLAS-ready economic
substrate, with deterministic core math, PQC, AEGIS governance, and a
refactored signal system. V13.8 extends this with user-as-value-node,
NFT-style content, new signal addons, governance observability, and
artistic/reputation-weighted policies.

> NOTE: This overview is descriptive. It does not redefine or replace the
> authoritative math/economics specs for individual engines.

## 1. Core Engine and Invariants

**Deterministic Core**

- `BigNum128`, `CertifiedMath`, `TreasuryEngine` /
  `TreasuryDistributionEngine`, `HarmonicEconomics`, `StateTransitionEngine`.
- All operations are integer-scaled, overflow-checked, fully logged, and
  replayable.

**Constitutional Guards**

- `EconomicsGuard`, `NODInvariantChecker`, CIR‑302 handler, AEGIS
  verification.
- Enforce Zero-Simulation, economic invariants, and governance firewalls.
- Violations trigger deterministic halts without rewriting history.

**Zero-Sim & PQC**

- AST Zero-Sim checker blocks floats, randomness, and wall-clock usage in
  consensus paths.
- PQC modules implement auditable serialization/signatures, ensuring
  cryptographic verifiability of ledger and signal operations.

## 2. Signals and SignalAddons

**HumorSignalAddon**

- 7-dimensional deterministic vector:
  - `chronos`, `lexicon`, `surreal`, `empathy`, `critique`, `slapstick`,
    `meta`.
- Aggregation and rewards occur **outside** the addon, via
  TreasuryEngine/policy only.

**ArtisticSignalAddon (V13.8)**

- Deterministic vector of:
  - `composition`, `originality_delta`, `emotional_resonance`, `craft`,
    `coherence_with_theme`.
- Effect gated by `ArtisticSignalPolicy`, activated only via governance vote
  weighted by ATR, FLX, and harmonic coherence (ΨSync).

**Governed Signals**

- All addons (humor, artistic, future) are deterministic evaluators.
- Reward effects must pass governance‑ratified policy rules.

## 3. User-as-Value-Node (V13.8 Feature)

- Each user is a deterministic **value node**, growing in value through
  coherent contributions (posts, comments, interactions).
- Every piece of content is an NFT-style object:
  - Versioned, content-addressed, and traceable.
  - Feeds ATR/FLX, coherence, and reward calculations into QFS.
- The network continuously updates user value, integrating:
  - NFT-content contributions.
  - Governance actions.
  - Signal interactions.

## 4. Governance and Observability Enhancements

**Signal Observatory**

- Dashboard for operators and advanced users to inspect signal
  distributions, correlations, and abuse patterns.
- Simulates policy changes before deployment.

**Explain-This Panels (User-Facing)**

- Transparent breakdown of rewards and rankings for posts and content:
  - Base reward, humor/artistic bonuses, coherence, guard passes.

**Harmonic Governance**

- Policy adjustments for signal weights, caps, and activation only via
  ATR/FLX + ΨSync-weighted votes.

## 5. Token Economics & Harmonic Invariants

- **Fixed harmonic token set**:
  - Users cannot create arbitrary tokens.
  - New tokens appear only via governance-approved mint paths and
    protocol-level TreasuryEngine logic.
- **Mint/burn rules**:
  - Deterministic, replayable, and validated against conservation
    invariants.
  - Fully logged in `TokenStateBundle`.
- Users can earn, transfer, or lock tokens, but minting is controlled by
  TreasuryEngine + governance rules.
- **Integration with signals**:
  - ATR/FLX rewards are calculated deterministically from signal vectors and
    user contributions, capped by governance policy.

## 6. Private Communication Layer (Secure Chat)

- **Open‑A.G.I Secure-Chat integration**:
  - End-to-end encrypted messaging with content-addressed storage
    (IPFS/StorageEngine) and on-chain hashes.
- **SecureChatEngine**:
  - QFS backend module for deterministic event logging, ATR fees,
    governance metadata; never sees plaintext.
- **AtlasSecureChatAdapter**:
  - Gateway API for thread creation, message append, metadata-only reads;
    front-end handles encryption/decryption.
- **Governance & Appeals**:
  - Secure-chat used for moderation appeals, node coordination, and
    governance discussions; metadata-only signals for OpenAGI advisory.

## 7. PQC, Telemetry, and AEGIS

- Deterministic PQC signing for all ledger, event, and signal data.
- Node telemetry:
  - Deterministic, auditable logging of participation and uptime.
- AEGIS verifies node identity and monitors aggregate metadata.
- OpenAGI consumes signals for advisories but cannot mutate live state.
- Telemetry feeds into harmonic coherence (ΨSync) for governance-weighted
  signal voting.

## 8. Testing, Compliance, and Replay

- Full unit, integration, and boundary-condition tests for:
  - Core deterministic math, treasury, and guards.
  - SignalAddons (humor, artistic).
  - NFT-content tracking and user-as-value-node accounting.
- Replay suite ensures deterministic reconstruction of:
  - Ledger events.
  - User scores and rewards.
- Zero-Sim and PQC reports confirm full compliance for deterministic
  execution and auditable signatures.

## 9. Economic Substrate Summary

- **User-centric rewards**:
  - Deterministic, traceable, harmonic- and policy-weighted.
- **NFT-style content**:
  - Every post/comment is a unique, auditable object contributing to
    system-wide value.
- **Signals and governance**:
  - Humor, artistic, coherence signals feed into rewards only after
    governance-approved policies.
- **Private communication**:
  - Secure, E2E encrypted, content-addressed chat integrates without
    affecting economic determinism.

## References / Evidence (V13.5 → V13.8)

- BigNum128/CertifiedMath core implementations & logs.
- HumorSignalAddon and ArtisticSignalAddon vectors.
- Zero-Sim compliance reports: `humor_zero_sim_report.json`,
  `base_zero_sim_report.json`.
- PQC modules: deterministic signing & DRV logging.
- SecureChatEngine & AtlasSecureChatAdapter design docs.
- Governance observability dashboards and Explain-This panel mockups.
- TokenStateBundle deterministic ATR/FLX reward logs.
- Replay test results: DeterministicReplayTest, BoundaryConditionTests,
  FailureModeTests.
