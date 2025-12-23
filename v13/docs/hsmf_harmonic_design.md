# HSMF Harmonic Design

**Version**: v13.5  
**Status**: Stable Core  
**Module**: `v13.core.HSMF`

## Overview

HSMF (Harmonic Stability & Action Cost Framework) provides a **deterministic scoring layer** for the QFS × ATLAS ecosystem. It computes action costs and reward allocations based on harmonic principles, ensuring economic stability while incentivizing coherent behavior.

---

## Theoretical Foundation

### The Five-Token Harmonic Model

QFS uses five token types, each representing a distinct aspect of system health:

| Token | Symbol | Role | HSMF Metric |
|-------|--------|------|-------------|
| **Coherence** | CHR | System stability | `s_chr` |
| **Flux** | FLX | Adaptation signal | `s_flx` |
| **Resistance** | RES | Friction measure | `s_res` |
| **Psi-Sync** | ΨSync | Temporal alignment | `s_psi_sync` |
| **ATR** | ATR | Transaction ratio | `f_atr` |

### Harmonic Stability Principle

> **"Actions that reduce system dissonance are rewarded; actions that increase dissonance bear higher costs."**

This principle drives all HSMF computations:

1. **Dissonance** = Sum of deviation metrics (S_RES + S_FLX + S_PSI_SYNC)
2. **Coherence Coefficient** (C_holo) = 1 / (1 + Dissonance)
3. **Action Cost** = f(Dissonance, λ weights, F_ATR)
4. **Rewards** = Per-token allocations scaled by C_holo

---

## Design Decisions

### Why C_holo Uses Inverse Proportion

The formula `c_holo = 1 / (1 + dissonance)` was chosen because:

1. **Bounded Output**: Always in (0, 1], preventing runaway rewards
2. **Monotonic Decay**: Higher dissonance → lower coefficient (predictable)
3. **Zero Dissonance = Maximum Coherence**: c_holo = 1 when system is perfectly aligned
4. **Asymptotic Approach**: Cannot reach zero, preventing complete reward elimination

### Why Separate Lambda Weights

The formula `action_cost = s_res + (λ₁ × s_flx) + (λ₂ × s_psi_sync) + f_atr` uses separate weights to:

1. **Policy Flexibility**: Governance can tune λ₁/λ₂ without code changes
2. **Token-Specific Sensitivity**: Different tokens may have different "cost" impacts
3. **Upgrade Path**: Future versions can add λ₃ for new metrics

---

## HSMF Flow Diagram

```mermaid
graph TD
    A[Action Request] --> B[Collect Metrics]
    B --> C{Compute Dissonance}
    C --> D[s_res + s_flx + s_psi_sync]
    D --> E[C_holo = 1 / (1 + Dissonance)]
    D --> F[Action Cost Formula]
    E --> G[Compute Rewards]
    F --> G
    G --> H[chr_reward = s_chr × c_holo]
    G --> I[flx_reward = s_flx × action_cost]
    G --> J[res_reward = s_res × c_holo]
    G --> K[psi_sync_reward = s_psi_sync × f_atr]
    G --> L[atr_reward = f_atr × c_holo]
    H --> M[Total Reward]
    I --> M
    J --> M
    K --> M
    L --> M
    M --> N[Emit HSMFProof]
    N --> O[Action Complete]
```

---

## Reward Allocation Logic

### Per-Token Reward Formulas

| Token | Formula | Interpretation |
|-------|---------|----------------|
| CHR | `s_chr × c_holo` | Coherence rewarded when system is harmonious |
| FLX | `s_flx × action_cost` | Flux traders benefit from high-activity states |
| RES | `s_res × c_holo` | Resistance holders rewarded during stability |
| ΨSync | `s_psi_sync × f_atr` | Sync contributors share in transaction flow |
| ATR | `f_atr × c_holo` | Transaction agents rewarded for harmonious trades |

### Why These Pairings?

- **CHR × c_holo**: Coherence holders are the "stability providers" — they should earn more when the system is stable
- **FLX × action_cost**: Flux represents change; higher action costs mean more change is happening, benefiting FLX holders
- **RES × c_holo**: Resistance acts as a damper; rewarded when system doesn't need much damping (high c_holo)
- **ΨSync × f_atr**: Temporal sync is tied to transaction flow, so it scales with ATR activity
- **ATR × c_holo**: Transaction participants are rewarded for executing in harmonious conditions

---

## Zero-Sim Compliance

HSMF is fully **Zero-Simulation Compliant**:

- ✅ **No Floats**: All arithmetic uses `BigNum128` (18-decimal fixed-point)
- ✅ **No Randomness**: Outputs are deterministic given inputs
- ✅ **No Wall-Clock Time**: Timestamps come from DRV packets, not `time.time()`
- ✅ **Replayable**: `test_hsmf_replay.py` proves bit-for-bit consistency
- ✅ **Auditable**: `HSMFProof` records capture all inputs/outputs

---

## Governance Parameters

| Parameter | Current Default | Description |
|-----------|-----------------|-------------|
| `lambda1` | 1 | Flux weight in action cost |
| `lambda2` | 1 | Psi-sync weight in action cost |
| `beta_penalty` | 100M (scaled) | Penalty multiplier for coherence deviation |
| `phi` | φ = 1.618... | Golden ratio for flux deviation target |

These can be adjusted via governance votes in future versions.

---

## Integration Points

### ATLAS Social Layer

HSMF is called by AEGIS (ATLAS Economic Governance Integration System) when:

1. User submits a post, comment, or reaction
2. AEGIS collects token states from user's bundle
3. HSMF computes action cost and reward allocation
4. RewardAllocator distributes tokens based on HSMF outputs

### CIR-302 Hard Failure

If HSMF validation fails (e.g., survival imperative violated), the `CIR302Handler` can:

1. Quarantine the action
2. Log a violation
3. Optionally revert partial state changes

---

## Related Documentation

- [HSMF_MathContracts.md](./HSMF_MathContracts.md) — Invariants and test specifications
- [HSMF_API.md](./HSMF_API.md) — Public API reference
- [tools/explain_hsmf_action.py](../tools/explain_hsmf_action.py) — CLI for human-readable explanations

---

*Last updated: 2025-12-23*
