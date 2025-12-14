# QFS × ATLAS Mission Constraints (V13.7–V13.8)

This document summarizes the shared mission and hard constraints that govern
QFS (the harmonic economic substrate) and ATLAS (the user- and operator-facing
application layer) for V13.7 and V13.8.

## 1. Fixed Harmonic Token Set

- The harmonic token set (e.g. QFS, ATR, FLX and protocol-defined companions)
  is **fixed and governed** at the protocol level.
- Neither V13.7 nor V13.8 introduce arbitrary new monetary tokens.
- All mint/burn and reallocation of token supply occurs only via:
  - `TreasuryEngine` / `TreasuryDistributionEngine`
  - Protocol-level governance and AEGIS-compliant upgrade paths

## 2. Value Flows Through Treasury + Guards

- All monetary value flows (balances, ATR/FLX changes) must pass through:
  - `BigNum128` / `CertifiedMath` for deterministic arithmetic
  - `TreasuryEngine`, `RewardAllocator`, `HarmonicEconomics`,
    `StateTransitionEngine`
  - Constitutional guards: `EconomicsGuard`, `NODInvariantChecker`,
    CIR-302 handler, and AEGIS verification
- No feature in ATLAS or V13.8 may bypass these engines or mutate core
  token balances directly.

## 3. V13.8 as Representational & Replay-Focused

- V13.8 introduces **user-as-value-node** and **content-as-NFT-style object**
  semantics:
  - `UserState` views over balances, ATR/FLX, coherence/ΨSync, governance
    footprint.
  - `content_id` for canonical, content-addressed assets.
  - A replayable **value graph** of `{users, content}` nodes and
    `{interactions, rewards, votes}` edges.
- These are **representational layers** over existing economics:
  - They do not mint new tokens.
  - They explain and attribute value flows that already occur via
    Treasury/Reward engines and guards.

## 4. Zero-Simulation and Deterministic Replay

- All consensus and economics-critical code must remain Zero-Sim compliant:
  - No use of wall-clock time, randomness, or non-deterministic I/O in
    state transitions.
  - Clocks, if used, must be injected and test-controlled.
- Ledger state, user value-node views, content-NFT state, and the value graph
  must be **replayable bit-for-bit** from:
  - The ordered ledger event log.
  - Deterministic policies and immutable configuration.

## 5. ATLAS Responsibilities

- ATLAS surfaces (APIs, UI, observability tools) must:
  - Present a clear, user-facing view of QFS state and value flows.
  - Use QFS as the single source of truth for balances and rewards.
  - Treat value-node and content-NFT constructs as read-only views over
    the underlying economics, except where explicitly governed policy
    allows new behaviour.
- ATLAS may **experiment safely** by:
  - Adding new observability and explanation layers (e.g. Explain-This,
    Value Graph Observatory).
  - Using V13.8 representational models to simulate policy changes **without
    mutating live state**.

## 6. Governance & Compliance Hooks

- Any change that affects how value-nodes, content events, or signal addons
  (humor, artistic, etc.) map into rewards must:
  - Be specified in policy documents.
  - Go through the established governance process.
  - Preserve deterministic replay and Zero-Sim constraints.
- Value-node and content-ID layers cannot be used to introduce new monetary
  instruments; they are attribution and observability tools on top of the
  harmonic token set.

---

**Cross-References**

- V13.7 scope: `docs/QFS_V13_7_SCOPE.md`
- V13.8 model: `specs/QFS_V13_8_VALUE_NODE_MODEL.md`
 - Integration plan: `docs/QFS_ATLAS_COHERENT_INTEGRATION_PLAN_V13_7_TO_V13_8.md`
