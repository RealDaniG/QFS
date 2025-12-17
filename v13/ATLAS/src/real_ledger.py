"""
RealLedger - Deterministic ledger adapter for QFS.

Provides a clean interface between QFS engines and underlying
ledger implementations (MockLedger, L1/L2, etc.).
"""
import json
import hashlib
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import logging
from .qfs_types import OperationBundle
logger = logging.getLogger(__name__)

@dataclass
class LedgerReceipt:
    """Receipt from ledger operations"""
    bundle_hash: str
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
class LedgerSnapshot:
    """Deterministic state snapshot"""
    state_root: str
    timestamp: str
    block_height: int
    state: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with sorted keys"""
        return json.loads(json.dumps(asdict(self), sort_keys=True))

class RealLedger:
    """
    Deterministic ledger adapter.
    
    Wraps underlying ledger implementations (MockLedger, L1/L2, etc.)
    and provides a consistent interface for QFS engines.
    """

    def __init__(self, adapter):
        """
        Initialize RealLedger.
        
        Args:
            adapter: Underlying ledger implementation (MockLedger, L1/L2 client)
        """
        self._adapter = adapter
        self._cache: Dict[str, Any] = {}

    async def submit_bundle(self, bundle: OperationBundle) -> LedgerReceipt:
        """
        Submit opaque bundle to underlying ledger.
        
        - Wait for deterministic confirmation
        - Return structured receipt
        
        Args:
            bundle: Bundle to submit
            
        Returns:
            LedgerReceipt: Structured receipt
        """
        try:
            if hasattr(self._adapter, 'bundles'):
                self._adapter.bundles[bundle.bundle_hash] = bundle
            receipt = await self._adapter.submit_bundle(bundle)
            self._cache[f'receipt:{bundle.bundle_hash}'] = receipt
            return receipt
        except Exception as e:
            logger.error(f'Failed to submit bundle: {e}')
            raise RuntimeError(f'Bundle submission failed: {e}')

    async def get_snapshot(self, state_root: Optional[str]=None) -> Dict[str, Any]:
        """
        Return deterministic state snapshot.
        
        Args:
            state_root: Optional state root to query
            
        Returns:
            Dict[str, Any]: Deterministic state
        """
        snapshot = await self._adapter.get_snapshot(state_root)
        return snapshot.state if hasattr(snapshot, 'state') else snapshot

    async def get_bundle(self, bundle_hash: str) -> Optional[Dict[str, Any]]:
        """Get bundle by hash"""
        try:
            return await self._adapter.get_bundle(bundle_hash)
        except Exception as e:
            logger.error(f'Failed to get bundle {bundle_hash}: {e}')
            return None

    async def get_bundle_status(self, bundle_hash: str) -> Dict[str, Any]:
        """Get bundle status"""
        try:
            return await self._adapter.get_bundle_status(bundle_hash)
        except Exception as e:
            logger.error(f'Failed to get bundle status {bundle_hash}: {e}')
            return {'status': 'error', 'error': str(e)}

    async def replay_bundle(self, bundle: OperationBundle) -> Dict[str, Any]:
        """Replay bundle for determinism verification"""
        try:
            return await self._adapter.replay_bundle(bundle)
        except Exception as e:
            logger.error(f'Failed to replay bundle {bundle.bundle_hash}: {e}')
            return {'success': False, 'error': str(e), 'divergence_details': ['replay_failed']}

    def clear_cache(self):
        """Clear internal cache"""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {'cached_items': len(self._cache), 'cache_size_bytes': sum((len(str(v)) for v in self._cache.values()))}