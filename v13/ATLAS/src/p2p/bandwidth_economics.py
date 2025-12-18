from fractions import Fraction
from v13.libs.economics.QAmount import QAmount
from typing import Dict, Any

class P2PBandwidthEconomics:
    """
    Track P2P bandwidth usage for NOD rewards.
    Implements Task 3.1 of QFS x ATLAS Security Integration.
    """

    def __init__(self, token_bundle=None):
        self.token_bundle = token_bundle
        self.bandwidth_metrics: Dict[str, Dict[str, int]] = {}

    def record_message_cost(self, peer_id: str, message_size: int, encrypted: bool):
        """
        Record bandwidth usage for NOD rewards.
        
        Args:
            peer_id: The remote peer ID
            message_size: Size of message in bytes
            encrypted: Whether the message was encrypted (bonus eligibility)
        """
        if peer_id not in self.bandwidth_metrics:
            self.bandwidth_metrics[peer_id] = {'sent': 0, 'received': 0, 'encrypted_count': 0}
        self.bandwidth_metrics[peer_id]['sent'] += message_size
        if encrypted:
            self.bandwidth_metrics[peer_id]['encrypted_count'] += 1

    def calculate_nod_reward(self, peer_id: str) -> QAmount:
        """
        Calculate NOD reward for P2P infrastructure node.
        
        Returns:
            Float representing NOD token amount earned.
        """
        metrics = self.bandwidth_metrics.get(peer_id, {})
        if not metrics:
            return 0
        total_bytes = metrics.get('sent', 0) + metrics.get('received', 0)
        total_mb = total_bytes / 1000000
        base_reward = total_mb * Fraction(1, 100)
        total_messages = metrics.get('encrypted_count', 0)
        encryption_bonus = Fraction(1, 10) if total_messages > 100 else 0
        return base_reward + encryption_bonus
