import hashlib
from typing import List, Dict, Any, Protocol
from abc import abstractmethod
from v15.crypto.adapter import sign_poe, verify_poe


class IBatchAnchorService(Protocol):
    """
    Interface for post-quantum anchoring of EvidenceBus segments.
    Provides batch signing capabilities for distributed Tier A nodes.
    """

    @abstractmethod
    def create_batch_signature(self, event_hashes: List[str]) -> Dict[str, Any]:
        """Produce a PQC signature for a sequence of event hashes."""
        ...

    @abstractmethod
    def verify_batch_signature(
        self, event_hashes: List[str], signature_hex: str
    ) -> bool:
        """Verify the PQC signature for a sequence of event hashes."""
        ...


class PQCBatchAnchorService:
    """
    Tier A Batch Anchor Service.
    Produces a single PQC-grounded signature for a segment of the EvidenceBus.
    """

    def create_batch_signature(self, event_hashes: List[str]) -> Dict[str, Any]:
        """
        Produce a deterministic batch signature.
        Uses a Merkle-root approximation for the segment.
        """
        # 1. Compute Batch Root (Deterministic)
        # We sort to ensure order-independence if needed, but EvidenceBus is ordered.
        # However, for batch anchoring, we follow the log order.
        combined = "".join(event_hashes).encode()
        batch_root = hashlib.sha3_256(combined).digest()

        # 2. Sign using PQC Adapter (Environment-Aware)
        signature = sign_poe(batch_root)

        return {
            "pqc_signature": signature.hex(),
            "algorithm": "v18-Dilithium-Anchor",
            "batch_root": batch_root.hex(),
            "event_count": len(event_hashes),
            "status": "anchored",
        }

    def verify_batch_signature(
        self, event_hashes: List[str], signature_hex: str
    ) -> bool:
        """Verify the anchor signature against the event list."""
        combined = "".join(event_hashes).encode()
        batch_root = hashlib.sha3_256(combined).digest()
        return verify_poe(batch_root, bytes.fromhex(signature_hex))


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

    def verify_batch_signature(
        self, event_hashes: List[str], signature_hex: str
    ) -> bool:
        return signature_hex.startswith("mock_pqc_sig_window_")
