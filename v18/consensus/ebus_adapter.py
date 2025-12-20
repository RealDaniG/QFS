from typing import Dict, Any, Protocol
# Note: v15.evidence.bus is the existing EvidenceBus implementation
# from v15.evidence.bus import EvidenceBus


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
    Adapter skeleton for v18 EvidenceBus integration.

    Design Rule: In a distributed Tier A cluster, EvidenceBus.append_event()
    is only called via this adapter's on_entry_committed callback.
    """

    def __init__(self, ebus: Any):  # Replace Any with EvidenceBus when wired
        self.ebus = ebus

    def on_entry_committed(self, entry: Dict[str, Any]) -> None:
        """
        Mock implementation of commitment handling.
        Actual implementation will extract the 'command' payload and
        invoke the EvidenceBus append logic.
        """
        # Example: self.ebus.append_event(entry["command"])
        pass
