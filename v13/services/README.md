# Services Directory

**Version**: v13.5  
**Last Updated**: 2025-12-23

This directory contains integration services for QFS × ATLAS.

---

## HSMF Integration Service

**File**: `hsmf_integration.py`

Provides the AEGIS → HSMF → RewardAllocator integration flow.

### Classes

| Class | Purpose |
|-------|---------|
| `HSMFIntegrationService` | Core integration service for HSMF pipeline |
| `HSMFActionResult` | Result dataclass with all computed metrics and proof |

### Usage

```python
from v13.services.hsmf_integration import HSMFIntegrationService
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128

cm = CertifiedMath()
service = HSMFIntegrationService(cm)

log_list = []
result = service.process_action(
    action_id="post_001",
    user_id="0xwallet",
    s_res=BigNum128.from_int(100),
    s_flx=BigNum128.from_int(50),
    s_psi_sync=BigNum128.from_int(75),
    f_atr=BigNum128.from_int(25),
    s_chr=BigNum128.from_int(800),
    lambda1=BigNum128.from_int(1),
    lambda2=BigNum128.from_int(1),
    log_list=log_list,
)

print(f"Action Cost: {result.action_cost.to_decimal_string()}")
print(f"C_holo: {result.c_holo.to_decimal_string()}")
print(f"Total Reward: {result.total_reward.to_decimal_string()}")
```

### Flow

```text
Input Metrics
    ↓
process_action()
    ↓
HSMF._calculate_action_cost_qfs()
HSMF._calculate_c_holo()
HSMF._compute_hsmf_rewards()
    ↓
HSMFProof emitted to log_list
    ↓
HSMFActionResult returned
```

### Tests

- `v13/tests/atlas/test_hsmf_wall_integration.py` — 8 integration tests

---

## AEGIS API

**File**: `aegis_api.py`

AEGIS (Autonomous Economic Governance Integration System) API for QFS transactions.

### Key Endpoints

- `/api/v1/transaction/validate` — Validate action bundle via HSMF
- `/api/v1/transaction/submit` — Submit validated transaction

---

## Related Documentation

- [HSMF_API.md](../docs/HSMF_API.md) — HSMF API surface
- [HSMF_MathContracts.md](../docs/HSMF_MathContracts.md) — Math invariants
- [hsmf_harmonic_design.md](../docs/hsmf_harmonic_design.md) — Theoretical grounding
