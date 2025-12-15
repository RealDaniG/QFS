"""
test_qfs_replay_source.py - Integration tests for QFSReplaySource adapter
"""

import pytest
from typing import Dict, Any
from v13.core.CoherenceLedger import CoherenceLedger
from v13.core.StorageEngine import StorageEngine
from v13.core.QFSReplaySource import QFSReplaySource
from v13.libs.CertifiedMath import CertifiedMath
from v13.core.TokenStateBundle import TokenStateBundle

def create_test_bundle(cm, timestamp=1234567890):
    """Helper to create a dummy token bundle."""
    return TokenStateBundle(
        chr_state={"coherence_metric": "0.98"},
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        signature="test_sig",
        timestamp=timestamp,
        bundle_id=f"bundle_{timestamp}",
        pqc_cid=f"pqc_{timestamp}",
        quantum_metadata={},
        lambda1=CertifiedMath.from_string("0.3"),
        lambda2=CertifiedMath.from_string("0.2"),
        c_crit=CertifiedMath.from_string("0.9"),
        parameters={}
    )

def test_replay_source_fetches_rewards():
    """Verify ReplaySource can find and format reward events."""
    # Setup Live Engines
    cm = CertifiedMath()
    ledger = CoherenceLedger(cm)
    storage = StorageEngine(cm)
    source = QFSReplaySource(ledger, storage)
    
    # 1. Log a reward to the ledger
    bundle = create_test_bundle(cm)
    rewards = {
        "CHR": {
            "token_name": "CHR",
            "amount": "100.0",
             # Embed wallet_id in the reward structure for the search to find it
             # Assuming standard QFS structure where wallet_id might be a key or in metadata
            "wallet_id": "wallet_123", 
            "details": "Reward for wallet_123"
        }
    }
    
    entry = ledger.log_state(
        token_bundle=bundle, 
        rewards=rewards, 
        deterministic_timestamp=1000
    )
    
    print(f"Logged entry {entry.entry_id} with type {entry.entry_type}")
    
    # 2. Query ReplaySource
    events = source.get_reward_events("wallet_123", epoch=1)
    
    # 3. Verify
    assert len(events) > 0, "Should find at least one event"
    reward_event = next(e for e in events if e["type"] == "RewardAllocated")
    assert reward_event["id"] == entry.entry_id
    assert "wallet_123" in str(reward_event)

def test_replay_source_missing_reward():
    """Verify ReplaySource returns empty list for missing rewards (Zero-Sim)."""
    cm = CertifiedMath()
    ledger = CoherenceLedger(cm)
    storage = StorageEngine(cm)
    source = QFSReplaySource(ledger, storage)
    
    events = source.get_reward_events("non_existent_wallet", epoch=1)
    assert events == []
