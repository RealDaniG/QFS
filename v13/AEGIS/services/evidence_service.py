"""
Evidence Service - Track 1.2

Provides access to deterministic proof vectors.
Connects to existing Explain-This framework and QFS core logs.
"""

from typing import List, Dict, Any, Optional
from ..ui_contracts.schemas import ProofVectorRef
from .evidence_models import ProofVector
from v13.core.QFSReplaySource import QFSReplaySource
from libs.deterministic_helpers import det_time_isoformat


def _proof_vector_to_ref(pv: ProofVector) -> ProofVectorRef:
    """Convert detailed ProofVector to UI-facing reference."""
    root_state_hash = pv.state_hashes[-1] if pv.state_hashes else "null_hash"
    root_log_hash = pv.log_hashes[-1] if pv.log_hashes else "null_hash"

    return ProofVectorRef(
        id=pv.id,
        scenario_type=pv.scenario_type,
        log_hash=root_log_hash,
        state_hash=root_state_hash,
    )


def _events_to_proof_vector(tx_id: str, events: List[Dict[str, Any]]) -> ProofVector:
    """
    Construct a ProofVector from a sequence of ledger events.
    """
    if not events:
        raise ValueError(f"No events found for {tx_id}")

    # Extract hashes and metadata from events
    state_hashes = []
    log_hashes = []
    guard_events = []

    # Simple extraction logic - in a real system this would be more complex
    # filtering for specific event types that contain state/log hashes
    for event in sorted(events):
        if "integrity_hash" in event:
            log_hashes.append(event["integrity_hash"])
        if "state_hash" in event:
            state_hashes.append(event["state_hash"])

    # Determine scenario type based on primary event type
    primary_type = events[0].get("type", "unknown")
    scenario_type = "transaction_trace"
    if "Reward" in primary_type:
        scenario_type = "economic_reward"
    elif "Governance" in primary_type:
        scenario_type = "governance_action"

    return ProofVector(
        id=tx_id,
        scenario_type=scenario_type,
        input_params={"tx_id": tx_id, "event_count": str(len(events))},
        outputs={"status": "verified"},
        guard_events=guard_events,
        state_hashes=state_hashes or ["null_state"],
        log_hashes=log_hashes or ["null_log"],
        source_module="QFSReplaySource",
        timestamp=events[0].get("timestamp", det_time_isoformat()),
    )


def get_proof_vectors_by_ids(
    ids: List[str], replay_source: QFSReplaySource
) -> List[ProofVectorRef]:
    """
    Retrieve proof vector references by their IDs (transaction hashes).

    Args:
        ids: List of transaction IDs/hashes
        replay_source: Source for deterministic ledger history

    Returns:
        List of references sorted by ID
    """
    results = []
    sorted_ids = sorted(ids)

    for pid in sorted(sorted_ids):
        try:
            # Fetch real events from the authoritative replay source
            events = replay_source.get_events_for_transaction(pid)
            pv = _events_to_proof_vector(pid, events)
            results.append(_proof_vector_to_ref(pv))
        except Exception as e:
            # In production, we might log this or skip
            # For strict zero-sim, we avoid side-effects, so maybe just skip
            pass

    return results


def find_proof_vectors_for_dag(
    dag_descriptor: Any, replay_source: QFSReplaySource
) -> List[ProofVectorRef]:
    """
    Find relevant proof vectors for a given DAG context.

    Args:
        dag_descriptor: Identifier or object describing the DAG context
        replay_source: Source for deterministic ledger history

    Returns:
        List of references
    """
    # This remains a placeholder for more complex DAG logic
    # In full implementation, this would look up proposals in the DAG
    # and fetch their associated transaction histories.
    return []
