"""
Storage Explainability Model for QFS V13.8

This module provides the data structures and verification logic for "Why is this stored here?"
explanations, replaying StorageEngine decisions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import hashlib
import json

@dataclass
class ContentStorageExplanation:
    """Detailed explanation of why content is stored on specific nodes."""
    content_id: str
    storage_nodes: List[str]  # AEGIS-verified node DIDs
    shard_ids: List[str]
    replica_count: int
    proof_outcomes: Dict[str, str]  # node_id -> "success" | "failed"
    epoch_assigned: int
    
    # Metadata
    integrity_hash: str = "" # SHA-3-256 of storage metadata
    policy_version: str = "v13.8.0"
    explanation_hash: str = ""
    
    def __post_init__(self):
        if not self.integrity_hash:
            self.integrity_hash = self._calculate_integrity_hash()
        if not self.explanation_hash:
            self.explanation_hash = self._calculate_explanation_hash()
    
    def _calculate_integrity_hash(self) -> str:
        """Calculate hash of critical storage metadata."""
        data = {
            "content_id": self.content_id,
            "nodes": sorted(self.storage_nodes),
            "shards": sorted(self.shard_ids),
            "epoch": self.epoch_assigned
        }
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def _calculate_explanation_hash(self) -> str:
        """Calculate full explanation hash for governance audit."""
        data = {
            "content_id": self.content_id,
            "storage_nodes": sorted(self.storage_nodes),
            "shard_ids": sorted(self.shard_ids),
            "replica_count": self.replica_count,
            "proof_outcomes": self.proof_outcomes,
            "epoch_assigned": self.epoch_assigned,
            "integrity_hash": self.integrity_hash,
            "policy_version": self.policy_version
        }
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

def explain_storage_placement(content_id: str, storage_events: List[Dict[str, Any]]) -> ContentStorageExplanation:
    """
    Replay storage events to explain why content is stored on specific nodes.
    Uses deterministic replica assignment from StorageEngine events.
    
    Args:
        content_id: CID of content
        storage_events: List of raw event dicts from ledger
    """
    # Replay logic (simplified for V13.8 rollout)
    nodes = set()
    shards = set()
    proofs = {}
    epoch = 0
    
    for event in storage_events:
        etype = event.get("type", "")
        payload = event.get("payload", {})
        
        if etype == "ContentStored":
            if payload.get("content_id") == content_id:
                epoch = event.get("epoch", 0)
                nodes.update(payload.get("nodes", []))
                shards.update(payload.get("shards", []))
                
        elif etype == "StorageProofSubmitted":
            if payload.get("content_id") == content_id:
                node_id = payload.get("node_id")
                outcome = "success" if payload.get("valid") else "failed"
                proofs[node_id] = outcome

    return ContentStorageExplanation(
        content_id=content_id,
        storage_nodes=list(sorted(nodes)),
        shard_ids=list(sorted(shards)),
        replica_count=len(nodes),
        proof_outcomes=proofs,
        epoch_assigned=epoch
    )
