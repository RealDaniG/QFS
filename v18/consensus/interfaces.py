from typing import Protocol, List, Optional, Any, Dict
from abc import abstractmethod


class IConsensusLog(Protocol):
    """Interface for the replicated deterministic log (EvidenceBus segment)."""

    @abstractmethod
    def append(self, entry: Dict[str, Any]) -> int:
        """Append entry and return index."""
        ...

    @abstractmethod
    def get_entries(
        self, start_index: int, end_index: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve entries from log."""
        ...

    @abstractmethod
    def last_index(self) -> int:
        """Get the index of the last entry."""
        ...

    @abstractmethod
    def last_term(self) -> int:
        """Get the term of the last entry."""
        ...


class IConsensusTransport(Protocol):
    """Interface for node-to-node communication."""

    @abstractmethod
    def send_rpc(
        self, target_node_id: str, rpc_name: str, payload: Dict[str, Any]
    ) -> Any:
        """Send a Remote Procedure Call to a peer node."""
        ...
