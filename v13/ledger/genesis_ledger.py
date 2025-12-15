
import hashlib
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import os

# In a real scenario, dependencies would be injected or imported from v13.core
# from v13.core.dependencies import get_crypto_engine (If needing signatures)

class GenesisEvent:
    """Represents a single immutable event in the Genesis Ledger."""
    def __init__(
        self,
        event_type: str,
        wallet: str,
        metadata: Dict[str, Any],
        signature: str,
        value: int = 0,
        epoch: int = 1,
        prev_hash: str = "0" * 64,
        id: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.id = id if id else str(uuid.uuid4())
        self.wallet = wallet
        self.epoch = epoch
        self.event_type = event_type
        self.value = value
        self.metadata = metadata
        self.signature = signature
        self.timestamp = timestamp if timestamp else datetime.now(timezone.utc).isoformat()
        self.prev_hash = prev_hash
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculates SHA3-512 hash of the event content + prev_hash."""
        payload = {
            "id": self.id,
            "wallet": self.wallet,
            "epoch": self.epoch,
            "event_type": self.event_type,
            "value": self.value,
            "metadata": self.metadata,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash
        }
        # Canonical JSON representation for hashing
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha3_512(payload_str.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "wallet": self.wallet,
            "epoch": self.epoch,
            "event_type": self.event_type,
            "value": self.value,
            "metadata": self.metadata,
            "hash": self.hash, # The event's own hash
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "signature": self.signature
        }

class GenesisLedger:
    """
    Append-only ledger for ATLAS Genesis events.
    Maintains a hash chain to ensure immutability.
    """
    def __init__(self, storage_path: str = "genesis_ledger.jsonl"):
        self.storage_path = storage_path
        self._last_hash = "0" * 64
        self._initialize_from_storage()

    def _initialize_from_storage(self):
        """Recover last hash from existing ledger file."""
        if not os.path.exists(self.storage_path):
            return

        with open(self.storage_path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        if "hash" in record:
                            self._last_hash = record["hash"]
                    except json.JSONDecodeError:
                        pass # Should log corruption

    def append_event(self, event_type: str, wallet: str, metadata: Dict[str, Any], signature: str, value: int = 0) -> GenesisEvent:
        """
        Create and append a new event to the ledger.
        """
        event = GenesisEvent(
            event_type=event_type,
            wallet=wallet,
            metadata=metadata,
            signature=signature,
            value=value,
            prev_hash=self._last_hash
        )

        with open(self.storage_path, 'a') as f:
            f.write(json.dumps(event.to_dict()) + "\n")
        
        self._last_hash = event.hash
        return event

    def verify_integrity(self) -> bool:
        """
        Replay the ledger and verify all hash chains.
        Returns True if valid, False if corruption detected.
        """
        if not os.path.exists(self.storage_path):
            return True

        expected_prev = "0" * 64
        valid = True
        
        with open(self.storage_path, 'r') as f:
            for line in f:
                if not line.strip(): continue
                
                try:
                    data = json.loads(line)
                    # Reconstruct event object to check hash
                    evt = GenesisEvent(
                         event_type=data['event_type'],
                         wallet=data['wallet'],
                         metadata=data['metadata'],
                         signature=data['signature'],
                         value=data['value'],
                         epoch=data['epoch'],
                         prev_hash=data['prev_hash'],
                         id=data['id'],
                         timestamp=data['timestamp']
                    )
                    
                    if evt.prev_hash != expected_prev:
                        print(f"Chain break detected at ID {evt.id}")
                        valid = False
                        break
                    
                    if evt.hash != data['hash']:
                        print(f"Hash mismatch at ID {evt.id}")
                        valid = False
                        break
                        
                    expected_prev = evt.hash
                    
                except Exception as e:
                    print(f"Error parsing line: {e}")
                    valid = False
                    break
                    
        return valid

    def get_events_for_wallet(self, wallet: str) -> List[Dict[str, Any]]:
        """Retrieve all events for a specific wallet."""
        results = []
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        if data.get('wallet') == wallet:
                            results.append(data)
                    except:
                        pass
        return results
