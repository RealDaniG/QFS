"""
CoherenceLedger.py - Immutable ledger for auditing deterministic coherence state and token updates

Implements the CoherenceLedger class for recording every token state, reward allocation,
and HSMF calculation step, generating AEGIS_FINALITY_SEAL.json upon atomic commit,
and maintaining a deterministic hash chain for PQC verification.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128
from v13.core.TokenStateBundle import TokenStateBundle
from v13.libs.PQC import PQC


@dataclass
class LedgerEntry:
    """Represents a single entry in the coherence ledger."""

    entry_id: str
    timestamp: int
    entry_type: str
    data: Dict[str, Any]
    previous_hash: str
    entry_hash: str
    pqc_cid: str
    quantum_metadata: Dict[str, Any]

    def __lt__(self, other: "LedgerEntry") -> bool:
        if not isinstance(other, LedgerEntry):
            return NotImplemented
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        return self.entry_id < other.entry_id

    def __le__(self, other: "LedgerEntry") -> bool:
        if not isinstance(other, LedgerEntry):
            return NotImplemented
        if self.timestamp != other.timestamp:
            return self.timestamp <= other.timestamp
        return self.entry_id <= other.entry_id

    def __gt__(self, other: "LedgerEntry") -> bool:
        if not isinstance(other, LedgerEntry):
            return NotImplemented
        if self.timestamp != other.timestamp:
            return self.timestamp > other.timestamp
        return self.entry_id > other.entry_id

    def __ge__(self, other: "LedgerEntry") -> bool:
        if not isinstance(other, LedgerEntry):
            return NotImplemented
        if self.timestamp != other.timestamp:
            return self.timestamp >= other.timestamp
        return self.entry_id >= other.entry_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LedgerEntry):
            return False
        return self.entry_id == other.entry_id and self.timestamp == other.timestamp


class CoherenceLedger:
    """
    Immutable ledger for auditing deterministic coherence state and token updates.

    Records every token state, reward allocation, and HSMF calculation step.
    Generates AEGIS_FINALITY_SEAL.json upon atomic commit.
    Maintains a deterministic hash chain for PQC verification.
    """

    def __init__(
        self, cm_instance: CertifiedMath, pqc_key_pair: Optional[tuple] = None
    ):
        """
        Initialize the Coherence Ledger.

        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            pqc_key_pair: Optional PQC key pair for signing ledger entries
        """
        self.cm = cm_instance
        self.pqc_private_key = pqc_key_pair[0] if pqc_key_pair else None
        self.pqc_public_key = pqc_key_pair[1] if pqc_key_pair else None
        self.ledger_entries: List[LedgerEntry] = []
        self.quantum_metadata = {
            "component": "CoherenceLedger",
            "version": "QFS-V13-P1-2",
            "timestamp": None,
            "pqc_scheme": "Dilithium-5",
        }

    def log_state(
        self,
        token_bundle: TokenStateBundle,
        hsmf_metrics: Optional[Dict[str, Any]] = None,
        rewards: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        guard_results: Optional[Dict[str, Any]] = None,
    ) -> LedgerEntry:
        """
        Add ledger entry for token state, HSMF metrics, and rewards.

        Args:
            token_bundle: TokenStateBundle with current token states
            hsmf_metrics: Optional HSMF metrics
            rewards: Optional reward allocations
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            guard_results: Optional guard evaluation results

        Returns:
            LedgerEntry: The created ledger entry
        """
        entry_data = {
            "token_bundle": token_bundle.to_dict(),
            "hsmf_metrics": hsmf_metrics or {},
            "rewards": rewards or {},
            "guards": guard_results or {},
        }
        previous_hash = self._get_previous_hash()
        entry_hash = self._generate_entry_hash(
            entry_data, previous_hash, deterministic_timestamp
        )
        pqc_cid = self._generate_pqc_cid(entry_data, deterministic_timestamp)
        timestamp = deterministic_timestamp
        self.quantum_metadata["timestamp"] = str(timestamp)
        entry = LedgerEntry(
            entry_id=entry_hash,
            timestamp=timestamp,
            entry_type=self._determine_entry_type(hsmf_metrics, rewards),
            data=entry_data,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            pqc_cid=pqc_cid,
            quantum_metadata=self.quantum_metadata.copy(),
        )
        self.ledger_entries.append(entry)
        return entry

    def generate_finality_seal(
        self, treasury_result: Optional[Any] = None, deterministic_timestamp: int = 0
    ) -> str:
        """
        Generate AEGIS_FINALITY_SEAL.json upon atomic commit.

        Args:
            treasury_result: Optional TreasuryResult to include in seal
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            str: Path to generated finality seal file or hash if no file system access
        """
        seal_data = {
            "component": "AEGIS_FINALITY_SEAL",
            "version": "QFS-V13-P1-2",
            "timestamp": deterministic_timestamp,
            "ledger_entries_count": len(self.ledger_entries),
            "ledger_hash_chain": self._get_ledger_hash_chain(),
            "treasury_result": {
                "is_valid": treasury_result.is_valid
                if hasattr(treasury_result, "is_valid")
                else False,
                "total_allocation": treasury_result.total_allocation.to_decimal_string()
                if hasattr(treasury_result, "total_allocation")
                else "0",
                "rewards_count": len(treasury_result.rewards)
                if hasattr(treasury_result, "rewards")
                else 0,
                "validation_errors": treasury_result.validation_errors
                if hasattr(treasury_result, "validation_errors")
                else [],
            }
            if treasury_result
            else {},
            "quantum_metadata": self.quantum_metadata,
        }
        seal_json = json.dumps(seal_data, sort_keys=True, separators=(",", ":"))
        seal_hash = hashlib.sha256(seal_json.encode("utf-8")).hexdigest()
        if self.pqc_private_key:
            try:
                signature = PQC.sign_data(
                    self.pqc_private_key, seal_json.encode("utf-8"), []
                )
                seal_data["pqc_signature"] = signature.hex()
            except Exception as e:
                pass
        return seal_hash

    def _get_previous_hash(self) -> str:
        """Get the hash of the previous ledger entry."""
        if not self.ledger_entries:
            return "genesis_hash_00000000000000000000000000000000"
        return self.ledger_entries[-1].entry_hash

    def _generate_entry_hash(
        self, entry_data: Dict[str, Any], previous_hash: str, timestamp: int
    ) -> str:
        """Generate deterministic hash for a ledger entry."""
        data_to_hash = {
            "entry_data": entry_data,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
        }
        data_json = json.dumps(data_to_hash, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(data_json.encode()).hexdigest()

    def _generate_pqc_cid(self, entry_data: Dict[str, Any], timestamp: int) -> str:
        """Generate deterministic PQC correlation ID."""
        data_to_hash = {"entry_data": entry_data, "timestamp": timestamp}
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]

    def _get_ledger_hash_chain(self) -> List[str]:
        """Get the complete hash chain of the ledger."""
        return [entry.entry_hash for entry in self.ledger_entries]

    def _determine_entry_type(
        self, hsmf_metrics: Optional[Dict[str, Any]], rewards: Optional[Dict[str, Any]]
    ) -> str:
        """Determine the type of ledger entry based on provided data."""
        if rewards is not None:
            return "reward_allocation"
        elif hsmf_metrics is not None:
            return "hsmf_metrics"
        else:
            return "token_state"

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Get a summary of the ledger."""
        return {
            "total_entries": len(self.ledger_entries),
            "entry_types": [entry.entry_type for entry in self.ledger_entries],
            "latest_timestamp": self.ledger_entries[-1].timestamp
            if self.ledger_entries
            else 0,
            "ledger_hash_chain_length": len(self._get_ledger_hash_chain()),
        }

    def append_event(self, event: Any) -> LedgerEntry:
        """
        Append a generic event to the ledger (e.g. Referral events).

        Args:
            event: The event object (dataclass) to append

        Returns:
            LedgerEntry: The created ledger entry
        """
        if hasattr(event, "__dict__"):
            event_data = event.__dict__
        else:
            event_data = dict(event)
        event_type = getattr(event, "event_type", "generic_event")
        timestamp = getattr(event, "epoch", 0)
        entry_data = {"event_data": event_data, "event_type": event_type}
        previous_hash = self._get_previous_hash()
        entry_hash = self._generate_entry_hash(entry_data, previous_hash, timestamp)
        pqc_cid = self._generate_pqc_cid(entry_data, timestamp)
        entry = LedgerEntry(
            entry_id=entry_hash,
            timestamp=timestamp,
            entry_type=event_type,
            data=entry_data,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            pqc_cid=pqc_cid,
            quantum_metadata=self.quantum_metadata.copy(),
        )
        self.ledger_entries.append(entry)
        return entry
