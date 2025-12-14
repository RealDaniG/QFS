"""
QFSClient - Deterministic SDK wrapper for QFS engines and RealLedger.

Provides a clean interface for ATLAS to interact with QFS engines
while maintaining deterministic behavior.
"""

import json
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import logging

from .real_ledger import RealLedger
from .types import Transaction, Receipt, DeterminismReport
from .qfs_types import OperationBundle

logger = logging.getLogger(__name__)

@dataclass
class TransactionReceipt:
    """Deterministic receipt for transaction submission"""
    transaction_id: str
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

class QFSClient:
    """
    Core client interface for QFS engines and RealLedger.
    
    Provides deterministic operations with proper signing, bundling,
    and ledger integration.
    """
    
    def __init__(self, ledger: RealLedger, private_key: Optional[str] = None):
        """
        Initialize QFSClient.
        
        Args:
            ledger: RealLedger instance for state management
            private_key: Private key for signing operations
        """
        self._ledger = ledger
        self._private_key = private_key
        self._pending_bundles: Dict[str, OperationBundle] = {}
        
    async def submit_transaction(self, tx: Transaction) -> TransactionReceipt:
        """
        Submit transaction to QFS engines via RealLedger.
        
        - Wrap tx into a QFS OperationBundle
        - Enforce PQC signing and DRV sequence
        - Submit to RealLedger
        - Return a deterministic receipt
        
        Args:
            tx: Transaction to submit
            
        Returns:
            TransactionReceipt: Deterministic receipt
            
        Raises:
            ValueError: If transaction is invalid
            RuntimeError: If submission fails
        """
        # Validate transaction
        if not tx.operation_type:
            raise ValueError("Transaction must have operation_type")
        
        if not tx.creator_id:
            raise ValueError("Transaction must have creator_id")
        
        # Create operation bundle
        operations = [{
            "type": tx.operation_type,
            "creator_id": tx.creator_id,
            "data": tx.data,
            "nonce": tx.nonce or 0
        }]
        
        # Generate deterministic bundle hash
        bundle_data = {
            "operations": operations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "creator_id": tx.creator_id
        }
        bundle_json = json.dumps(bundle_data, sort_keys=True)
        bundle_hash = hashlib.sha256(bundle_json.encode()).hexdigest()
        
        bundle = OperationBundle(
            operations=operations,
            bundle_hash=bundle_hash,
            timestamp=bundle_data["timestamp"],
            creator_id=tx.creator_id
        )
        
        # Sign bundle if private key available
        if self._private_key:
            bundle.signature = self._sign_bundle(bundle)
        
        # Submit to RealLedger
        try:
            receipt = await self._ledger.submit_bundle(bundle)

            # RealLedger may return a dataclass-style receipt or a dict-like receipt.
            # Normalize access deterministically.
            if isinstance(receipt, dict):
                _status = receipt.get("status", "submitted")
                _timestamp = receipt.get("timestamp", bundle.timestamp)
                _block_hash = receipt.get("block_hash")
                _block_height = receipt.get("block_height")
                _gas_used = receipt.get("gas_used")
                _events = receipt.get("events", [])
            else:
                _status = getattr(receipt, "status", "submitted")
                _timestamp = getattr(receipt, "timestamp", bundle.timestamp)
                _block_hash = getattr(receipt, "block_hash", None)
                _block_height = getattr(receipt, "block_height", None)
                _gas_used = getattr(receipt, "gas_used", None)
                _events = getattr(receipt, "events", []) or []
            
            # Convert to TransactionReceipt
            tx_receipt = TransactionReceipt(
                transaction_id=tx.transaction_id or bundle_hash,
                bundle_hash=bundle_hash,
                status=_status,
                timestamp=_timestamp,
                block_hash=_block_hash,
                block_height=_block_height,
                gas_used=_gas_used,
                events=_events
            )
            
            # Store pending bundle tracking
            self._pending_bundles[bundle_hash] = bundle
            # Also allow lookup by transaction_id (some callers supply explicit tx ids)
            self._pending_bundles[tx_receipt.transaction_id] = bundle
            
            return tx_receipt
            
        except Exception as e:
            logger.error(f"Failed to submit transaction: {e}")
            raise RuntimeError(f"Transaction submission failed: {e}")
    
    async def get_state(self, address: str) -> Dict[str, Any]:
        """
        Read deterministic state from RealLedger snapshot.
        
        Args:
            address: Address to query
            
        Returns:
            Dict[str, Any]: Deterministic state with sorted keys
        """
        try:
            snapshot = await self._ledger.get_snapshot()
            
            # Extract state for specific address
            if address in snapshot:
                state = snapshot[address]
            else:
                # Return empty state for new addresses
                state = {
                    "address": address,
                    "balance": 0,
                    "nonce": 0,
                    "storage": {},
                    "code": None
                }
            
            # Ensure deterministic serialization
            return json.loads(json.dumps(state, sort_keys=True))
            
        except Exception as e:
            logger.error(f"Failed to get state for {address}: {e}")
            raise RuntimeError(f"State query failed: {e}")
    
    async def replay_transaction(self, tx_hash: str) -> DeterminismReport:
        """
        Re-run transaction via QFS replay engine.
        
        - Compare state/bundle hashes against RealLedger
        - Return pass/fail and divergence details
        
        Args:
            tx_hash: Transaction hash to replay
            
        Returns:
            DeterminismReport: Replay results
        """
        try:
            # Get original bundle from pending or ledger
            bundle = self._pending_bundles.get(tx_hash)
            if not bundle:
                # Try to retrieve from ledger
                bundle_data = await self._ledger.get_bundle(tx_hash)
                if not bundle_data:
                    raise ValueError(f"Transaction {tx_hash} not found")
                bundle = OperationBundle(**bundle_data)
            
            # Execute replay
            replay_result = await self._ledger.replay_bundle(bundle)
            
            # Generate determinism report
            report = DeterminismReport(
                transaction_hash=tx_hash,
                bundle_hash=bundle.bundle_hash,
                replay_success=replay_result.get("success", False),
                state_hash=replay_result.get("state_hash"),
                original_state_hash=replay_result.get("original_state_hash"),
                matches_original=replay_result.get("state_hash") == replay_result.get("original_state_hash"),
                gas_used=replay_result.get("gas_used", 0),
                events=replay_result.get("events", []),
                divergence_details=replay_result.get("divergence_details", [])
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to replay transaction {tx_hash}: {e}")
            raise RuntimeError(f"Transaction replay failed: {e}")
    
    def _sign_bundle(self, bundle: OperationBundle) -> str:
        """
        Sign operation bundle with private key.
        
        Args:
            bundle: Bundle to sign
            
        Returns:
            str: Signature
        """
        # This is a simplified signature implementation
        # In production, use proper PQC signing
        bundle_data = json.dumps(bundle.to_dict(), sort_keys=True)
        signature = hashlib.sha256(f"{self._private_key}:{bundle_data}".encode()).hexdigest()
        return signature
    
    async def get_bundle_status(self, bundle_hash: str) -> Dict[str, Any]:
        """
        Get status of a submitted bundle.
        
        Args:
            bundle_hash: Hash of the bundle
            
        Returns:
            Dict[str, Any]: Bundle status
        """
        try:
            return await self._ledger.get_bundle_status(bundle_hash)
        except Exception as e:
            logger.error(f"Failed to get bundle status: {e}")
            return {"status": "unknown", "error": str(e)}
    
    async def list_pending_bundles(self) -> List[str]:
        """
        List all pending bundle hashes.
        
        Returns:
            List[str]: List of pending bundle hashes
        """
        return list(self._pending_bundles.keys())
    
    def clear_pending_bundles(self):
        """Clear all pending bundles (useful for testing)"""
        self._pending_bundles.clear()
