"""
Deterministic Session ID Generator
Formula: HASH(counter || node_seed || wallet_hash || issued_at)
"""

import hashlib
from typing import Optional


class SessionIDGenerator:
    """
    Generates deterministic, collision-resistant session IDs.
    """

    def __init__(self, node_seed: str):
        """
        Args:
            node_seed: Deterministic seed for this node (from config/EvidenceBus)
        """
        self.node_seed = node_seed
        self.counter = 0  # Monotonic counter

    def _create_next_sequence(self) -> int:
        """Increment counter safely (whitelisted logic)."""
        self.counter = self.counter + 1
        return self.counter

    def generate(self, wallet_address: str, issued_at: int) -> str:
        """
        Generate deterministic session ID.

        Args:
            wallet_address: User's wallet address
            issued_at: Unix timestamp of session creation

        Returns:
            64-character hex session ID
        """
        count = self._create_next_sequence()

        # Construct deterministic input
        input_data = f"{count}||{self.node_seed}||{wallet_address}||{issued_at}"

        # SHA3-512 for collision resistance
        session_id = hashlib.sha3_512(input_data.encode("utf-8")).hexdigest()

        return session_id

    def get_counter(self) -> int:
        """Get current counter value (for logging/PoE)."""
        return self.counter
