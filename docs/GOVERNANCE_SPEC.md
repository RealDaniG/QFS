# Protocol Governance Specification

**Current Status: Implemented (v17+ Capability Baseline)**

## The "Self-Amending" Protocol

The QFS implementation features a constitutional governance layer where the protocol upgrades its own parameters through a deterministic, audit-proof process.

## Architecture

### 1. The Constitution (Immutable)

Core protocol invariants and logic are **Constitutionally Protected** and cannot be changed by governance:

- **Zero-Simulation Logic**: Determinism is the fundamental invariant of the system.
- **PQC Signatures**: Post-Quantum Cryptographic security primitives are fixed at the core.
- **Inflation Caps**: Hard ceilings on emission rates (e.g., `CHR_DAILY_EMISSION_CAP`) are enforced by the protocol constitution.

### 2. The Registry (Mutable)

A specific set of operational parameters is whitelisted for governance-managed updates:

- `VIRAL_POOL_CAP`: Adjusting the flow of rewards to viral content.
- `FLX_REWARD_FRACTION`: Tuning the flux distribution.
- `ATR_BASE_COST`: Adjusting anti-spam economics.

### 3. The Cycle

The governance process follows a strict, index-based state machine implemented in v16/v17:

1. **Proposal Period**: Submit hash-bound proposal to the EvidenceBus.
2. **Voting Period**: Node operators cast weighted votes.
3. **Cooldown**: Period for automated simulation and final audit checking.
4. **Adoption**: Automatic execution if Quorum and Supermajority requirements are met.

## Implementation Status

- **ViralRewardBinder**: Implementation reads strictly from the Governance Registry.
- **RewardAllocator**: Implementation observes Registry state for emission limits and budget enforcement.
- **EvidenceBus Integration**: All governance events are anchored in the Class A EvidenceBus for full auditability.
