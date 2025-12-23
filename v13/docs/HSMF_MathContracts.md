# HSMF Math Contracts Specification

**Version**: v13.5  
**Module**: `v13.core.HSMF`  
**Dependencies**: `v13.libs.BigNum128`, `v13.libs.CertifiedMath`

## Purpose

HSMF (Harmonic Stability & Action Cost Framework) is a **deterministic scoring engine** for social actions (posts, comments, interactions) in the ATLAS ecosystem. It computes:

1. **Action Cost** — Energy required for an action based on coherence metrics
2. **C_holo** — Holistic coefficient measuring system harmony
3. **Reward Allocation** — Token-specific rewards based on metrics

All computations use `BigNum128` fixed-point arithmetic (18 decimal places) and are fully **Zero-Sim compliant**: no randomness, no floats, no wall-clock dependencies.

---

## Core Functions

### `_calculate_action_cost_qfs`

Computes the energy cost of an action.

**Inputs**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `s_res` | BigNum128 | Resistance metric (effective interest) |
| `s_flx` | BigNum128 | Flux deviation from φ (golden ratio) |
| `s_psi_sync` | BigNum128 | Psi sync deviation |
| `f_atr` | BigNum128 | ATR factor |
| `λ₁` | BigNum128 | Flux weight multiplier |
| `λ₂` | BigNum128 | Psi sync weight multiplier |

**Formula**:

```text
action_cost = s_res + (λ₁ × s_flx) + (λ₂ × s_psi_sync) + f_atr
```

**Output**: `BigNum128` representing the action cost.

---

### `_calculate_c_holo`

Computes the holistic coefficient — a measure of system coherence.

**Inputs**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `s_res` | BigNum128 | Resistance metric |
| `s_flx` | BigNum128 | Flux deviation |
| `s_psi_sync` | BigNum128 | Psi sync deviation |

**Formula**:

```text
total_dissonance = s_res + s_flx + s_psi_sync
c_holo = 1 / (1 + total_dissonance)
```

**Output**: `BigNum128` in range `(0, 1]`.

**Invariant**: C_holo = 1 when dissonance = 0; strictly decreases as dissonance increases.

---

### `_compute_hsmf_rewards`

Computes per-token reward allocations based on HSMF metrics.

**Inputs**: Dict containing `s_chr`, `c_holo`, `s_res`, `s_flx`, `s_psi_sync`, `f_atr`, `action_cost`.

**Formulas**:

```text
chr_reward     = s_chr × c_holo
flx_reward     = s_flx × action_cost
res_reward     = s_res × c_holo
psi_sync_reward = s_psi_sync × f_atr
atr_reward     = f_atr × c_holo
total_reward   = sum of all above
```

**Output**: Dict with per-token rewards and `total_reward`.

---

## Invariants (Tested)

The following contracts are enforced by `test_hsmf_math_contracts.py`:

### Action Cost Monotonicity

- ✅ If `s_res` increases (other inputs fixed), action cost must increase
- ✅ If `s_flx` increases (other inputs fixed), action cost must increase
- ✅ If `λ₁` increases (with `s_flx > 0`), action cost must increase

### Coherence Bounds

- ✅ `c_holo` must be in `(0, 1]`
- ✅ `c_holo = 1` when total dissonance = 0
- ✅ `c_holo` strictly decreases as dissonance increases

### Reward Invariants

- ✅ Higher `c_holo` → higher `chr_reward` (for same `s_chr`)
- ✅ `total_reward` = sum of `chr_reward + flx_reward + res_reward + psi_sync_reward + atr_reward`

### Determinism

- ✅ Identical inputs must produce identical `action_cost` (bit-for-bit)
- ✅ Identical inputs must produce identical `c_holo` (bit-for-bit)

---

## Crypto-Agnostic Math Layer

HSMF math tests mock PQC (Post-Quantum Cryptography) dependencies:

```python
# In conftest.py
_dummy_pqc = types.ModuleType("PQC")
_dummy_pqc.sign = lambda *args, **kwargs: b"mock_signature"
_dummy_pqc.verify = lambda *args, **kwargs: True
sys.modules.setdefault("v13.libs.PQC", _dummy_pqc)
```

**Why mock PQC?**

- HSMF math contracts are **independent of cryptographic operations**
- Tests verify algebraic properties (monotonicity, bounds, determinism)
- Avoids requiring `liboqs` native libraries for math-only validation
- Keeps CI fast and portable across environments

**Safe because**:

- PQC is only used for signing/verification, not for HSMF computations
- All HSMF inputs are already validated before reaching the engine
- Mock behavior (`verify() → True`) matches happy-path execution

---

## Replay Tests

HSMF determinism is enforced by `test_hsmf_replay.py`:

- **Fixed Fixture**: 5 synthetic actions with varying metrics
- **Bit-for-bit Determinism**: Same inputs → identical outputs across runs
- **Stable Hash Anchor**: SHA-256 of outputs for regression detection
- **Invariant Checks**: Positive outputs, reward sum conservation, zero dissonance handling

---

## PoE Logging

HSMF emits structured `HSMFProof` entries for auditing:

```python
@dataclass
class HSMFProof:
    action_id: str
    user_id: str
    inputs: {s_res, s_flx, s_psi_sync, f_atr, s_chr, lambda1, lambda2}
    outputs: {action_cost, c_holo, chr_reward, flx_reward, res_reward, 
              psi_sync_reward, atr_reward, total_reward}
    hsmf_version: str = "v13.5"
```

Emitted via `hsmf._emit_hsmf_poe(proof, log_list)` as a pure side-effect.

---

## Related Documentation

- [HSMF_API.md](./HSMF_API.md) — Public API surface
- [hsmf_harmonic_design.md](./hsmf_harmonic_design.md) — Theoretical grounding
- [services/hsmf_integration.py](../services/hsmf_integration.py) — Integration service
- [atlas/wall/hsmf_wall_service.py](../atlas/wall/hsmf_wall_service.py) — Wall integration

---

## ATLAS Social Integration (v13.5)

These math contracts are now **enforced in the live ATLAS wall pipeline**:

1. **Entry Point**: `HSMFWallService.create_scored_post()` (posts, quotes, reactions)
2. **HSMF Evaluation**: `HSMFIntegrationService.process_action()` computes all metrics
3. **PoE Emission**: `HSMFProof` logged for every action
4. **Result**: `ScoredPost` returned with post + HSMF metrics

**Integration Tests**: `v13/tests/atlas/test_hsmf_wall_integration.py` (8 tests)

**Default f_atr Tiers**:

| Action | Default f_atr | Cost Impact |
|--------|---------------|-------------|
| Posts | 10 | Baseline |
| Quotes | 15 | Higher engagement |
| Reactions | 1 | Minimal |

## Future: Property-Based Testing

The following invariants are candidates for Hypothesis-style property tests:

1. **Monotonicity**: Generate random `BigNum128` pairs `(a, b)` where `a < b`, verify `cost(a) ≤ cost(b)`
2. **Bounds**: Generate random dissonance values, verify `0 < c_holo ≤ 1`
3. **Determinism**: Generate random inputs, run twice, assert `hash(output₁) == hash(output₂)`
4. **Reward Conservation**: Generate random metrics, verify `sum(parts) == total`

These would use:

```python
from hypothesis import given, strategies as st

@given(s_res=st.integers(0, 10**12), s_flx=st.integers(0, 10**12))
def test_action_cost_monotonic_hypothesis(s_res, s_flx):
    # ... property test implementation
```

> **Note**: Property-based tests are not yet implemented. This section serves as a design blueprint for future hardening.

---

*Last updated: 2025-12-23*
