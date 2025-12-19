"""
Governance Index Manager for v15.3 PoE
Manages the append-only, hash-chained index of governance execution proofs.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class GovernanceIndexManager:
    """
    Manages the hash-chained governance index.
    Ensures integrity and append-only semantics for PoE artifacts.
    """

    def __init__(self, index_file: str = "evidence/governance_index.json"):
        self.index_path = Path(index_file)
        self.max_entries_per_file = 1000  # For future pagination support
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create initial index file if it doesn't exist."""
        if not self.index_path.exists():
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            initial_index = {
                "index_version": "1.0",
                "chain_start_hash": self._sha3_512(b"GENESIS_QFS_V15"),
                "entries": [],
                "chain_head_hash": self._sha3_512(b"GENESIS_QFS_V15"),
                "total_entries": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
            }
            self._save_index(initial_index)

    def _sha3_512(self, data: bytes) -> str:
        """Generate SHA3-512 hash."""
        h = hashlib.sha3_512()
        h.update(data)
        return f"sha3_512:{h.hexdigest()}"

    def _canonical_serialize(self, data: Any) -> str:
        """Canonical JSON serialization."""
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def _load_index(self) -> Dict[str, Any]:
        """Load the current index."""
        with open(self.index_path, "r") as f:
            return json.load(f)

    def _save_index(self, index_data: Dict[str, Any]):
        """Save the index data atomically."""
        # Write to temp file then rename to ensure atomicity
        temp_path = self.index_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(index_data, f, indent=2, sort_keys=True)
        temp_path.replace(self.index_path)

    def add_entry(self, artifact: Dict[str, Any]) -> str:
        """
        Append a new PoE artifact to the governance index.
        Computes hash chain linking this entry to the previous head.

        Args:
            artifact: The PoE artifact dictionary to index.

        Returns:
            The new chain head hash.
        """
        index = self._load_index()

        previous_head = index["chain_head_hash"]
        sequence_number = index["total_entries"] + 1

        # Create index entry structure
        entry = {
            "sequence_number": sequence_number,
            "artifact_id": artifact["artifact_id"],
            "epoch": artifact["governance_scope"]["epoch"],
            "cycle": artifact["governance_scope"]["cycle"],
            "scope": artifact["governance_scope"]["parameter_key"],
            "phase": artifact["execution_phase"],
            "proof_hash": artifact["proof_hash"],
            "previous_entry_hash": previous_head,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "retrieval_path": f"evidence/poe_artifacts/{artifact['artifact_id']}.json",
        }

        # Compute hash of this entry (including link to previous)
        entry_content_hash = self._sha3_512(self._canonical_serialize(entry).encode())
        entry["this_entry_hash"] = entry_content_hash

        # Update index state
        index["entries"].append(entry)
        index["chain_head_hash"] = entry_content_hash
        index["total_entries"] = sequence_number
        index["last_updated"] = datetime.utcnow().isoformat() + "Z"

        self._save_index(index)
        return entry_content_hash

    def verify_chain(self) -> bool:
        """
        Verify the complete integrity of the hash chain.
        Returns True if valid, False otherwise.
        """
        index = self._load_index()
        current_hash = index["chain_start_hash"]

        for entry in index["entries"]:
            # 1. Check link to previous
            if entry["previous_entry_hash"] != current_hash:
                print(
                    f"Chain Broken at Seq {entry['sequence_number']}: Prev Hash Mismatch"
                )
                return False

            # 2. Recompute hash of this entry
            # Create a copy without the hash itself to verify
            verify_entry = entry.copy()
            stored_hash = verify_entry.pop("this_entry_hash")

            computed_hash = self._sha3_512(
                self._canonical_serialize(verify_entry).encode()
            )

            if computed_hash != stored_hash:
                print(f"Chain Corrupt at Seq {entry['sequence_number']}: Hash Mismatch")
                return False

            current_hash = stored_hash

        # 3. Verify head matches last entry
        if current_hash != index["chain_head_hash"]:
            print("Chain Head Mismatch")
            return False

        return True

    def get_by_scope(self, parameter_key: str) -> List[Dict[str, Any]]:
        """Retrieve all entries for a specific parameter."""
        index = self._load_index()
        return [e for e in index["entries"] if e["scope"] == parameter_key]


# Global instance pattern
_index_manager = None


def get_index_manager() -> GovernanceIndexManager:
    global _index_manager
    if _index_manager is None:
        _index_manager = GovernanceIndexManager()
    return _index_manager
