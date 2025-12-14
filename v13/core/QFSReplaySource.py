"""
QFSReplaySource.py - Read-Only Adapter for QFS Ledger History
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# Absolute imports to ensure zero-sim compliance (no mocks)
from v13.core.CoherenceLedger import CoherenceLedger, LedgerEntry
from v13.core.StorageEngine import StorageEngine

class QFSReplaySource:
    """
    Read-only adapter that fetches immutable history from CoherenceLedger and StorageEngine.
    Used by ValueNodeReplayEngine to reconstruct state for 'Explain-This' queries.
    
    Invariant: Zero-Simulation. No random numbers, no wall-clock time, no side effects.
    """
    
    def __init__(self, ledger: CoherenceLedger, storage: StorageEngine):
        """
        Initialize with references to the authoritative ledger and storage.
        """
        self.ledger = ledger
        self.storage = storage

    def get_events_for_transaction(self, tx_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve the sequence of events associated with a specific transaction/entry ID.
        
        Args:
            tx_id: The hash/ID of the target ledger entry (e.g. a RewardAllocation entry).
            
        Returns:
            List[Dict]: A list of event dictionaries suitable for replay.
        """
        # 1. Find the target entry in the ledger
        # In a real system with DB, this would be a query. 
        # Here we iterate the in-memory strictly-ordered list.
        target_entry: Optional[LedgerEntry] = None
        target_index = -1
        
        for i, entry in enumerate(self.ledger.ledger_entries):
            if entry.entry_id == tx_id:
                target_entry = entry
                target_index = i
                break
        
        if not target_entry:
            # Fallback: Check if it's an older entry in Storage (not implemented in this slice)
            raise ValueError(f"Transaction ID {tx_id} not found in active CoherenceLedger.")

        # 2. Extract context. 
        # For a thorough replay, we might need X preceding events or the last snapshot.
        # For V13.8 explainability, we primarily need the 'reward_allocation' event 
        # and the 'hsmf_metrics' event that likely preceded it or is part of the same block.
        
        events = []
        
        # Look back for the most recent HSMF metrics if not in current entry
        # This naive lookback assumes proximity.
        context_window = self.ledger.ledger_entries[max(0, target_index - 5) : target_index + 1]
        
        for entry in context_window:
            # Flatten entry data into an "Event" format expected by ReplayEngine
            # We map LedgerEntry to the cleaner "Event" dict.
            
            base_event = {
                "id": entry.entry_id,
                "timestamp": entry.timestamp,
                "type": entry.entry_type,
                # Flatten the data payload
                **entry.data 
            }
            
            # Specific mapping for Replay compatibility
            if entry.entry_type == "reward_allocation":
                 base_event["type"] = "RewardAllocated"
                 # Ensure 'amount' and 'wallet_id' are accessible if strictly required by keys
                 # The 'rewards' dict in entry.data might need unpacking
            
            elif entry.entry_type == "hsmf_metrics":
                 base_event["type"] = "MetricsUpdate"
                 
            events.append(base_event)
            
        return events

    def get_reward_events(self, wallet_id: str, epoch: int) -> List[Dict[str, Any]]:
        """
        Find and retrieve the events for a reward allocation by wallet and epoch.
        Performs a linear scan (in this slice) to find the matching entry.
        """
        target_entry_id = None
        
        # Linear scan for the specific reward entry
        for entry in self.ledger.ledger_entries:
            if entry.entry_type == "reward_allocation":
                 # Check if this entry corresponds to the requested wallet/epoch
                 # We assume the `log_state` call included `wallet_id` in `rewards` dict values
                 raw_data = str(entry.data.get("rewards", ""))
                 if wallet_id in raw_data:
                     # Found it. Get context.
                     return self.get_events_for_transaction(entry.entry_id)
                     
        return []

    def get_ranking_events(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve events related to Content Ranking for a specific content ID.
        """
        # This would require indexing by content_id.
        # For Phase 2, we linear scan the ledger for entries containing this content_id in metadata.
        events = []
        for entry in self.ledger.ledger_entries:
            # Check metadata or payload
            # Hypothetical structure match
            if str(entry.data.get("content_id")) == content_id:
                 events.append({
                     "id": entry.entry_id,
                     "timestamp": entry.timestamp,
                     "type": "ContentInteraction", # Generic type for replay
                     **entry.data
                 })
        return events

    def get_storage_events(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve storage-related events for a content ID.
        Includes initial 'ContentStored' and subsequent 'StorageProofSubmitted'.
        """
        events = []
        # Linear scan for V13.8 (optimize with indices in V14)
        for entry in self.ledger.ledger_entries:
            # Check for ContentStored
            if entry.entry_type == "content_stored":
                if str(entry.data.get("content_id")) == content_id:
                     events.append({
                         "id": entry.entry_id,
                         "timestamp": entry.timestamp,
                         "type": "ContentStored",
                         "payload": entry.data,
                         "epoch": 1 # Default epoch for this slice if not in data
                     })
            
            # Check for StorageProofs
            elif entry.entry_type == "storage_proof":
                 if str(entry.data.get("content_id")) == content_id:
                     events.append({
                         "id": entry.entry_id,
                         "timestamp": entry.timestamp,
                         "type": "StorageProofSubmitted",
                         "payload": entry.data
                     })
                     
        return events


class LiveLedgerReplaySource(QFSReplaySource):
    """
    Production-grade Replay Source that reads from disk-persisted Ledger artifacts.
    Replaces in-memory references with a parsed local copy of the immutable ledger.
    """
    
    def __init__(self, ledger_path: str, storage: StorageEngine):
        """
        Initialize by loading the ledger from disk.
        
        Args:
            ledger_path: Path to the .jsonl ledger file
            storage: Reference to StorageEngine (can also be read-only/hydrated)
        """
        self.ledger_path = ledger_path
        
        # Hydrate a read-only CoherenceLedger from disk
        from v13.core.CoherenceLedger import CoherenceLedger, LedgerEntry
        from v13.libs.CertifiedMath import CertifiedMath
        
        # Use a fresh CM instance for parsing
        cm = CertifiedMath()
        self.ledger = CoherenceLedger(cm, pqc_key_pair=None)
        
        self._load_ledger_from_disk()
        
        # Pass hydrated ledger to parent
        super().__init__(self.ledger, storage)
        
    def _load_ledger_from_disk(self) -> None:
        """Parse JSONL file and populate self.ledger.ledger_entries."""
        import os
        from v13.core.CoherenceLedger import LedgerEntry
        
        if not os.path.exists(self.ledger_path):
            raise FileNotFoundError(f"Ledger artifact not found at: {self.ledger_path}")
            
        entries = []
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                        
                    data = json.loads(line)
                    
                    # Reconstruct LedgerEntry object
                    # We assume the JSONL format matches LedgerEntry fields
                    # Handle potential schema mismatch gracefully if needed
                    
                    entry = LedgerEntry(
                        entry_id=data.get("entry_id"),
                        timestamp=data.get("timestamp"),
                        entry_type=data.get("entry_type"),
                        data=data.get("data", {}),
                        previous_hash=data.get("previous_hash"),
                        entry_hash=data.get("entry_hash"),
                        pqc_cid=data.get("pqc_cid"),
                        quantum_metadata=data.get("quantum_metadata", {})
                    )
                    entries.append(entry)
                    
            self.ledger.ledger_entries = entries
            # print(f"Hydrated LiveLedgerReplaySource with {len(entries)} entries from {self.ledger_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse live ledger from {self.ledger_path}: {e}")

