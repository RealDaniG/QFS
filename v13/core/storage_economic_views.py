from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

from v13.libs.CertifiedMath import BigNum128, CertifiedMath


@dataclass(frozen=True)
class StorageMetricsView:
    epoch: int
    bytes_stored_per_node: Dict[str, BigNum128]
    proofs_generated_per_node: Dict[str, int]
    proof_failures: int


def compute_storage_metrics_from_events(events: List[Mapping[str, Any]]) -> StorageMetricsView:
    """Compute read-only storage metrics from StorageEvents only.

    This is a pure function intended for observability and replay-derived views.
    It does not touch network/disk and does not mutate any engine state.

    Notes on alignment with current StorageEngine metrics semantics:
    - StorageEngine increments node.bytes_stored by *full content_size* for each
      shard assignment (not by per-shard chunk length). We mirror that here.
    """

    cm = CertifiedMath()

    current_epoch = 0
    bytes_stored_per_node: Dict[str, BigNum128] = {}
    proofs_generated_per_node: Dict[str, int] = {}
    proof_failures = 0

    for ev in events:
        event_type = ev.get("event_type")

        if event_type == "EPOCH_ADVANCEMENT":
            current_epoch = int(ev.get("epoch") or 0)
            continue

        if event_type == "STORE":
            content_size = int(ev.get("content_size") or 0)
            replica_sets = ev.get("replica_sets") or {}

            for _, nodes in sorted(replica_sets.items()):
                for node_id in nodes:
                    prev = bytes_stored_per_node.get(node_id, BigNum128.from_int(0))
                    bytes_stored_per_node[node_id] = cm.add(prev, BigNum128.from_int(content_size), [])
            continue

        if event_type == "PROOF_GENERATED":
            replica_sets = ev.get("replica_sets") or {}
            for _, nodes in sorted(replica_sets.items()):
                for node_id in nodes:
                    proofs_generated_per_node[node_id] = proofs_generated_per_node.get(node_id, 0) + 1
            continue

        if event_type == "PROOF_FAILED":
            proof_failures += 1
            continue

    return StorageMetricsView(
        epoch=current_epoch,
        bytes_stored_per_node=bytes_stored_per_node,
        proofs_generated_per_node=proofs_generated_per_node,
        proof_failures=proof_failures,
    )
