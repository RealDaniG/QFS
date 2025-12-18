"""Shared QFS types to avoid circular imports.

OperationBundle is used by both qfs_client and real_ledger.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import json

@dataclass
class OperationBundle:
    """Bundle of operations to be submitted to RealLedger.

    This is intentionally isolated in qfs_types to avoid circular
    imports between qfs_client and real_ledger.
    """
    operations: List[Dict[str, Any]]
    bundle_hash: str
    timestamp: str
    creator_id: str
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with sorted keys for determinism."""
        data = asdict(self)
        return json.loads(json.dumps(data, sort_keys=True))
