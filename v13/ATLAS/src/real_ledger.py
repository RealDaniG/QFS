"""
RealLedger - Deterministic ledger adapter for QFS.

Provides a clean interface between QFS engines and underlying
ledger implementations (MockLedger, L1/L2, etc.).
"""

import json
import hashlib
import asyncio
from datetime import datetime, timezone
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

class MockLedger:
    """Mock ledger implementation for testing"""
    
    def __init__(self):
        self.bundles: Dict[str, OperationBundle] = {}
        self.blocks: List[Dict[str, Any]] = []
        self.current_height = 0
        self.state: Dict[str, Any] = {}
        
    async def submit_bundle(self, bundle: OperationBundle) -> LedgerReceipt:
        """Submit bundle to mock ledger"""
        # Store bundle in mock ledger
        self.bundles[bundle.bundle_hash] = bundle
        self.current_height += 1
        block_hash = hashlib.sha256(f"block_{self.current_height}".encode()).hexdigest()
        
        # Process operations
        for op in bundle.operations:
            if op["type"] == "secure_chat_thread_created":
                creator_id = op["creator_id"]
                if creator_id not in self.state:
                    self.state[creator_id] = {
                        "address": creator_id,
                        "balance": 1000,
                        "nonce": 0,
                        "storage": {},
                        "code": None
                    }
                # Update nonce
                self.state[creator_id]["nonce"] += 1
                
        return LedgerReceipt(
            bundle_hash=bundle.bundle_hash,
            status="confirmed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            block_hash=block_hash,
            block_height=self.current_height,
            gas_used=21000,
            events=[{"event": "bundle_processed", "bundle_hash": bundle.bundle_hash}]
        )
    
    async def get_snapshot(self, state_root: Optional[str] = None) -> LedgerSnapshot:
        """Get state snapshot from mock ledger"""
        state_hash = hashlib.sha256(
            json.dumps(self.state, sort_keys=True).encode()
        ).hexdigest()
        
        return LedgerSnapshot(
            state_root=state_root,
            timestamp=datetime.now(timezone.utc).isoformat(),
            block_height=self.current_height,
            state=self.state.copy()
        )
    
    async def get_bundle(self, bundle_hash: str) -> Optional[Dict[str, Any]]:
        """Get bundle by hash"""
        if bundle_hash in self.bundles:
            return asdict(self.bundles[bundle_hash])
        return None
    
    async def get_bundle_status(self, bundle_hash: str) -> Dict[str, Any]:
        """Get bundle status"""
        if bundle_hash in self.bundles:
            return {
                "status": "confirmed",
                "block_height": self.current_height
            }
        return {"status": "not_found"}
    
    async def replay_bundle(self, bundle: OperationBundle) -> Dict[str, Any]:
        """Replay bundle for determinism check"""
        # Simulate deterministic measurement
        original_hash = hashlib.sha256(
            json.dumps(self.state, sort_keys=True).encode()
        ).hexdigest()
        
        # Simulate replay
        replay_state = self.state.copy()
        for op in bundle.operations:
            if op["type"] == "secure_chat_thread_created":
                creator_id = op["creator_id"]
                if creator_id not in replay_state:
                    replay_state[creator_id] = {
                        "address": creator_id,
                        "balance": 1000,
                        "nonce": 0,
                        "storage": {},
                        "code": None
                    }
                replay_state[creator_id]["nonce"] += 1
        
        new_hash = hashlib.sha256(
            json.dumps(replay_state, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "success": True,
            "state_hash": new_hash,
            "original_state_hash": original_hash,
            "gas_used": 21000,
            "events": [{"event": "bundle_replayed", "bundle_hash": bundle["bundle_hash"]}],
            "divergence_details": [] if new_hash == original_hash else ["state_diverged"]
        }

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
            # Store bundle for replay
            if hasattr(self._adapter, 'bundles'):
                self._adapter.bundles[bundle.bundle_hash] = bundle
            
            # Submit to adapter
            receipt = await self._adapter.submit_bundle(bundle)
            
            # Cache receipt
            self._cache[f"receipt:{bundle.bundle_hash}"] = receipt
            
            return receipt
            
        except Exception as e:
            logger.error(f"Failed to submit bundle: {e}")
            raise RuntimeError(f"Bundle submission failed: {e}")
    
    async def get_snapshot(self, state_root: Optional[str] = None) -> Dict[str, Any]:
        """
        Return deterministic state snapshot.
        
        Args:
            state_root: Optional state root to query
            
        Returns:
            Dict[str, Any]: Deterministic state
        """
        # Get snapshot from adapter
        snapshot = await self._adapter.get_snapshot(state_root)
        
        # Return deterministic state
        return snapshot.state if hasattr(snapshot, 'state') else snapshot
        
    async def get_bundle(self, bundle_hash: str) -> Optional[Dict[str, Any]]:
        """Get bundle by hash"""
        try:
            return await self._adapter.get_bundle(bundle_hash)
        except Exception as e:
            logger.error(f"Failed to get bundle {bundle_hash}: {e}")
            return None
    
    async def get_bundle_status(self, bundle_hash: str) -> Dict[str, Any]:
        """Get bundle status"""
        try:
            return await self._adapter.get_bundle_status(bundle_hash)
        except Exception as e:
            logger.error(f"Failed to get bundle status {bundle_hash}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def replay_bundle(self, bundle: OperationBundle) -> Dict[str, Any]:
        """Replay bundle for determinism verification"""
        try:
            return await self._adapter.replay_bundle(bundle)
        except Exception as e:
            logger.error(f"Failed to replay bundle {bundle.bundle_hash}: {e}")
            return {
                "success": False,
                "error": str(e),
                "divergence_details": ["replay_failed"]
            }
    
    def clear_cache(self):
        """Clear internal cache"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cached_items": len(self._cache),
            "cache_size_bytes": sum(len(str(v)) for v in self._cache.values())
        }
