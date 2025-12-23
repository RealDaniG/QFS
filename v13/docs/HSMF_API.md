# HSMF API Surface Documentation

**Version**: v13.5  
**File**: `v13/core/HSMF.py`  
**Lines**: 720+  
**Last Updated**: 2025-12-23

## Public Classes

### `ValidationResult`

Result dataclass from HSMF validation.

| Field | Type | Description |
|-------|------|-------------|
| `is_valid` | `bool` | Overall validation passed |
| `dez_ok` | `bool` | Directional encoding check passed |
| `survival_ok` | `bool` | Survival imperative (S_CHR ≥ C_CRIT) |
| `errors` | `List[str]` | Validation error messages |
| `raw_metrics` | `Dict[str, BigNum128]` | Computed HSMF metrics |

---

### `HSMFProof` (v13.5)

Proof-of-Evaluation (PoE) record for HSMF computations.

| Field | Type | Description |
|-------|------|-------------|
| `action_id` | `str` | Unique action identifier |
| `user_id` | `str` | User/wallet identifier |
| `s_res`, `s_flx`, `s_psi_sync`, `f_atr`, `s_chr` | `str` | Inputs (decimal strings) |
| `lambda1`, `lambda2` | `str` | Weights (decimal strings) |
| `action_cost`, `c_holo` | `str` | Core outputs |
| `chr_reward`, `flx_reward`, `res_reward`, `psi_sync_reward`, `atr_reward`, `total_reward` | `str` | Per-token rewards |
| `hsmf_version` | `str` | Version string (e.g., "v13.5") |

See: [HSMF_MathContracts.md](./HSMF_MathContracts.md) for schema details.

---

### `HSMF`

Main HSMF engine class.

#### Constructor

```python
HSMF(
    cm_instance: CertifiedMath,
    cir302_handler: Optional[CIR302_Handler] = None,
    state_transition_engine: Optional[StateTransitionEngine] = None
)
```

#### Public Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `validate_action_bundle(...)` | `ValidationResult` | Main validation entry point |
| `apply_hsmf_transition(...)` | `TokenStateBundle` | Atomic 5-token state update |
| `_emit_hsmf_poe(proof, log_list)` | `None` | Emit HSMFProof to log (v13.5) |

---

## Internal Methods (Core Math)

| Method | Maps To | Formula |
|--------|---------|---------
| `_calculate_action_cost_qfs()` | `compute_energy_cost` | `s_res + λ₁·s_flx + λ₂·s_psi_sync + f_atr` |
| `_calculate_c_holo()` | Coherence | `1 / (1 + s_res + s_flx + s_psi_sync)` |
| `_calculate_I_eff()` | S_RES (resistance) | `β · (1 - S_CHR)²` |
| `_calculate_delta_lambda()` | S_FLX (flux deviation) | Deviation from φ (golden ratio) |
| `_calculate_delta_h()` | S_PSI_SYNC | Sequence deviation |
| `_compute_hsmf_rewards()` | Token weights | Reward allocation per token type |

---

## ATLAS Social Integration (v13.5)

HSMF is now integrated into the ATLAS wall pipeline:

```
post/quote/reaction
    ↓
HSMFWallService.create_scored_post()
    ↓
HSMFIntegrationService.process_action()
    ↓
HSMF (cost + c_holo + rewards)
    ↓
HSMFProof → log_list
    ↓
ScoredPost returned
```

**Integration Files**:

- `v13/services/hsmf_integration.py` — Core integration service
- `v13/atlas/wall/hsmf_wall_service.py` — HSMF-enabled wall posts

**Tests**: `v13/tests/atlas/test_hsmf_wall_integration.py` (8 tests)

---

## Call Sites

### Production (4+)

- `v13/services/aegis_api.py:494` — `validate_action_bundle()`
- `v13/sdk/QFSV13SDK.py:129` — `validate_action_bundle()`
- `v13/services/hsmf_integration.py` — Full HSMF pipeline
- `v13/atlas/wall/hsmf_wall_service.py` — Wall post scoring

### Verification (30+ total)

- `v13/tests/HSMF/test_hsmf_math_contracts.py` — 13 invariant tests
- `v13/tests/HSMF/test_hsmf_replay.py` — 9 replay/PoE tests
- `v13/tests/atlas/test_hsmf_wall_integration.py` — 8 integration tests
- `v13/tools/explain_hsmf_action.py` — CLI explainer

---

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `ONE` | `1.0` | BigNum128 unit |
| `ZERO` | `0.0` | BigNum128 zero |
| `ONE_PERCENT` | `0.01` | 1% in BigNum128 scale |
| `PHI` | `1.618...` | Golden ratio |

---

## Dependencies

- `CertifiedMath` (deterministic arithmetic)
- `TokenStateBundle` (token state container)
- `StateTransitionEngine` (atomic updates)
- `RewardAllocator` (reward distribution)
- `CIR302_Handler` (error handling/quarantine)

---

## Related Documentation

- [HSMF_MathContracts.md](./HSMF_MathContracts.md) — Invariants and test specifications
- [hsmf_harmonic_design.md](./hsmf_harmonic_design.md) — Theoretical grounding
- [tools/explain_hsmf_action.py](../tools/explain_hsmf_action.py) — CLI explainer
