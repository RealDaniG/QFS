# Storage Policy Templates (Draft/Inactive)

These are **draft governance proposal templates** for storage-related policies. They are **inactive** and **non-enforced** until explicitly activated by governance.

---

## Template A: Storage Reliability Weighting (Draft)

**Objective**: Adjust future NOD reward formulas to weight node reliability.

**Metrics (read-only, replay-derived)**:
- Bytes stored per epoch (from `compute_storage_metrics_from_events`)
- Proof success rate per node
- Proof failure count per epoch

**Proposed weighting formula (inactive)**:
```
reliability_weight = (bytes_stored / total_bytes) * (proof_success_rate / 1.0)
```

**Status**: Draft / Inactive / Non-enforced

**Activation path**: Requires governance vote with quorum and policy version bump.

---

## Template B: Proof Quality Thresholds (Draft)

**Objective**: Define minimum proof success rates for nodes to be eligible for future rewards.

**Thresholds (inactive)**:
- Minimum proof success rate: 95%
- Minimum proof attempts per epoch: 10
- Maximum allowed proof failures per epoch: 2

**Status**: Draft / Inactive / Non-enforced

**Activation path**: Requires governance vote and audit trail.

---

## Template C: Future NOD Reward Formula (Draft)

**Objective**: Outline a deterministic reward formula for NOD operators based on storage contribution and proof reliability.

**Variables (read-only, replay-derived)**:
- `bytes_stored_per_node`
- `proof_success_rate_per_node`
- `epoch_duration`
- `global_storage_budget`

**Proposed formula (inactive)**:
```
nod_reward = global_storage_budget *
  (bytes_stored_per_node / total_bytes_stored) *
  (proof_success_rate_per_node / 1.0)
```

**Status**: Draft / Inactive / Non-enforced

**Activation path**: Requires governance vote, economic audit, and TreasuryEngine integration.

---

## Governance Process Notes

- All templates are **read-only** until activated.
- Activation requires a **governance proposal** with explicit versioning.
- Economic effects must route through **TreasuryEngine** and **PolicyRegistry**.
- Audit trails must be preserved for replay verification.
- No UI or API may enforce these policies until activated.

---

## Implementation Readiness

- `compute_storage_metrics_from_events` provides the required inputs.
- `StorageEngine` events are replayable and deterministic.
- `ATLAS` can surface these as observability dashboards without enforcement.
- Future wiring to TreasuryEngine must respect guard invariants.
