"""
Common types for QFS and ATLAS integration.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class Transaction:
    """Transaction structure for QFS operations"""
    transaction_id: Optional[str]
    operation_type: str
    creator_id: str
    data: Dict[str, Any]
    nonce: Optional[int] = None
    signature: Optional[str] = None

@dataclass
class Receipt:
    """Generic receipt structure"""
    transaction_id: str
    status: str
    timestamp: str
    block_hash: Optional[str] = None
    block_height: Optional[int] = None
    gas_used: Optional[int] = None
    events: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.events is None:
            self.events = []

@dataclass
class DeterminismReport:
    """Report from transaction replay verification"""
    transaction_hash: str
    bundle_hash: str
    replay_success: bool
    state_hash: Optional[str]
    original_state_hash: Optional[str]
    matches_original: bool
    gas_used: int
    events: List[Dict[str, Any]]
    divergence_details: List[str]