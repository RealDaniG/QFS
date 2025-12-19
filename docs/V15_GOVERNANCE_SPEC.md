# v15 Autonomous Governance Specification

## The "Self-Amending" Protocol

QFS v15 introduces a constitutional governance layer where the protocol can upgrade its own parameters through a deterministic, audit-proof process.

## Architecture

### 1. The Constitution (Immutable)

Certain parameters and logic are **Constitutionally Protected** and cannot be changed by governance:

- **Zero-Simulation Logic**: Determinism is non-negotiable.
- **PQC Signatures**: Security primitives are fixed.
- **Inflation Caps**: Hard ceilings on emission rates (e.g., `CHR_DAILY_EMISSION_CAP` cannot be removed, only lowered if mutable).

### 2. The Registry (Mutable)

A subset of parameters is whitelisted for governance:

- `VIRAL_POOL_CAP`: Adjusting the flow of rewards to viral content.
- `FLX_REWARD_FRACTION`: Tuning the flux distribution.
- `ATR_BASE_COST`: Adjusting anti-spam economics.

### 3. The Cycle (Tezos-Inspired)

The governance process follows a strict, index-based state machine:

1. **Proposal Period**: Submit hash-bound proposal.
2. **Voting Period**: NOD holders cast weighted votes.
3. **Cooldown**: Time for simulation and audit.
4. **Adoption**: Automatic execution if Quorum & Supermajority valid.

## Integration

- **ViralRewardBinder**: Reads strictly from the Governance Registry.
- **RewardAllocator**: Observes Registry state for emission limits.
