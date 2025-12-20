from typing import Dict, Any, Protocol
from v15.evidence.bus import EvidenceBus


class IConsensusEvidenceAdapter(Protocol):
    """
    Interface definition for binding consensus commitments to EvidenceBus.
    This ensures that only majority-verified events enter the canonical record.
    """

    def on_entry_committed(self, entry: Dict[str, Any]) -> None:
        """
        Callback triggered when a log entry achieves majority quorum.
        Must result in a deterministic append to the local EvidenceBus.
        """
        ...


class EvidenceBusConsensusAdapter:
    """
    Adapter for v18 EvidenceBus integration.

    Bridging Raft commitment to the canonical EvidenceBus.
    """

    def __init__(self):
        # We use the class-level EvidenceBus directly as it is a singleton/utility class
        pass

    def on_entry_committed(self, entry: Dict[str, Any]) -> None:
        """Forward committed entry to EvidenceBus."""
        command = entry.get("command", {})
        if not command:
            return

        event_type = command.get("type", "UNKNOWN_ACTION")
        payload = command.get("payload", {})

        # Inject consensus metadata for auditability
        payload["v18_consensus_term"] = entry.get("term", 0)

        # Forward to EvidenceBus
        EvidenceBus.emit(event_type, payload)
