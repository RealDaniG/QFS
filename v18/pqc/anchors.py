from typing import List, Dict, Any, Protocol
from abc import abstractmethod


class IBatchAnchorService(Protocol):
    """
    Interface for post-quantum anchoring of EvidenceBus segments.
    Provides batch signing capabilities for distributed Tier A nodes.
    """

    @abstractmethod
    def create_batch_signature(self, event_hashes: List[str]) -> Dict[str, Any]:
        """
        Produce a PQC signature for a sequence of event hashes.

        Args:
            event_hashes: List of deterministic hashes from EvidenceBus segments.

        Returns:
            Dictionary containing:
                - pqc_signature: Hex-encoded signature blob.
                - algorithm: ID or name of the PQC scheme (e.g., 'Dilithium2').
                - anchor_id: Logical ID for the batch.
        """
        ...


class MockBatchAnchorService:
    """
    Simulated PQC anchor service for development and testing.
    Standardizes on the 'MOCK-PQC' label for zero-sim compliance in dev envs.
    """

    def create_batch_signature(self, event_hashes: List[str]) -> Dict[str, Any]:
        """Returns a deterministic mock signature."""
        return {
            "pqc_signature": "mock_pqc_sig_window_" + str(len(event_hashes)),
            "algorithm": "MOCK-Dilithium2",
            "anchor_status": "BETA-MOCK",
        }
