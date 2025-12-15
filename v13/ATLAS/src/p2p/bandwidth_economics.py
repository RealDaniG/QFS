
from typing import Dict, Any

# Initial placeholder for token bundle integration
# from v13.core.TokenStateBundle import TokenStateBundle

class P2PBandwidthEconomics:
    """
    Track P2P bandwidth usage for NOD rewards.
    Implements Task 3.1 of QFS x ATLAS Security Integration.
    """
    
    def __init__(self, token_bundle=None):
        self.token_bundle = token_bundle
        # peer_id -> {"sent": bytes, "received": bytes, "encrypted_count": int}
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
            self.bandwidth_metrics[peer_id] = {"sent": 0, "received": 0, "encrypted_count": 0}
        
        # Accumulate usage. Note: sender/receiver logic depends on call context.
        # Assuming this tracks cost *incurred* by interacting with peer_id 
        # (or attribution to that node if it is relaying).
        # For simplicity, we track volume associated with the peer connection.
        self.bandwidth_metrics[peer_id]["sent"] += message_size 
        
        if encrypted:
            self.bandwidth_metrics[peer_id]["encrypted_count"] += 1
    
    def calculate_nod_reward(self, peer_id: str) -> float:
        """
        Calculate NOD reward for P2P infrastructure node.
        
        Returns:
            Float representing NOD token amount earned.
        """
        metrics = self.bandwidth_metrics.get(peer_id, {})
        if not metrics:
            return 0.0
            
        # Base reward: 0.01 NOD per MB of encrypted traffic
        total_bytes = metrics.get("sent", 0) + metrics.get("received", 0)
        total_mb = total_bytes / 1_000_000
        base_reward = total_mb * 0.01
        
        # Bonus for high encryption rate (>100 messages)
        # This incentivizes active, secure participation
        total_messages = metrics.get("encrypted_count", 0)
        encryption_bonus = 0.1 if total_messages > 100 else 0.0
        
        return base_reward + encryption_bonus
