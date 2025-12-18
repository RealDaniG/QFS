"""
ATLAS Economic Event - Canonical Definition

Canonical representation of economic events for QFS integration.
Used by Spaces, Wall Posts, and other ATLAS modules.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class EconomicEvent:
    """Economic event for QFS integration"""

    event_id: str
    event_type: str
    wallet_id: str
    token_type: str
    amount: str
    timestamp: int
    metadata: Dict[str, Any]
    pqc_signature: str
