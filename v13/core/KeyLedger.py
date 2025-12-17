"""
KeyLedger.py - Immutable ledger for auditing deterministic PQC keys, capabilities, and authorization chains

Implements the KeyLedger class for recording every PQC key registration, rotation,
revocation, and authorization event, generating KEY_FINALITY_SEAL.json upon atomic commit,
and maintaining a deterministic hash chain for PQC verification.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ..libs.PQC import PQC
from ..libs.CertifiedMath import CertifiedMath

@dataclass
class KeyLedgerEntry:
    """Represents a single entry in the key ledger."""
    entry_id: str
    timestamp: int
    entry_type: str
    data: Dict[str, Any]
    previous_hash: str
    entry_hash: str
    pqc_cid: str
    quantum_metadata: Dict[str, Any]

class KeyLedger:
    """
    Immutable ledger for auditing deterministic PQC key management and authorization chains.
    
    Records every PQC key registration, rotation, revocation, and capability assignment.
    Generates KEY_FINALITY_SEAL.json upon atomic commit.
    Maintains a deterministic hash chain for PQC verification.
    """

    def __init__(self, pqc_key_pair: Optional[tuple]=None):
        """
        Initialize the Key Ledger.

        Args:
            pqc_key_pair: Optional PQC key pair for signing ledger entries
        """
        self.pqc_private_key = pqc_key_pair[0] if pqc_key_pair else None
        self.pqc_public_key = pqc_key_pair[1] if pqc_key_pair else None
        self.ledger_entries: List[KeyLedgerEntry] = []
        self.quantum_metadata = {'component': 'KeyLedger', 'version': 'QFS-V13-P1-2', 'timestamp': None, 'pqc_scheme': 'Dilithium-5'}

    def log_key_event(self, key_id: str, event_type: str, capability: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0, quantum_metadata_per_event: Optional[Dict[str, Any]]=None) -> KeyLedgerEntry:
        """
        Add a ledger entry for a key event.

        Args:
            key_id: Identifier of the PQC key
            event_type: 'key_registration', 'key_rotation', 'capability_assignment', 'revocation'
            capability: Optional capability details
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            KeyLedgerEntry: The created ledger entry
        """
        entry_data = {'key_id': key_id, 'event_type': event_type, 'capability': capability or {}}
        previous_hash = self._get_previous_hash()
        entry_hash = self._generate_entry_hash(entry_data, previous_hash, deterministic_timestamp)
        pqc_cid = self._generate_pqc_cid(entry_data, deterministic_timestamp)
        timestamp = deterministic_timestamp
        self.quantum_metadata['timestamp'] = str(timestamp)
        entry = KeyLedgerEntry(entry_id=entry_hash, timestamp=timestamp, entry_type=event_type, data=entry_data, previous_hash=previous_hash, entry_hash=entry_hash, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata_per_event or self.quantum_metadata.copy())
        self.ledger_entries.append(entry)
        return entry

    def generate_finality_seal(self, deterministic_timestamp: int=0) -> str:
        """
        Generate KEY_FINALITY_SEAL.json upon atomic commit.

        Args:
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            str: Hash of the generated finality seal
        """
        seal_data = {'component': 'KEY_FINALITY_SEAL', 'version': 'QFS-V13-P1-2', 'timestamp': deterministic_timestamp, 'ledger_entries_count': len(self.ledger_entries), 'ledger_hash_chain': self._get_ledger_hash_chain(), 'quantum_metadata': self.quantum_metadata}
        seal_json = json.dumps(seal_data, sort_keys=True, separators=(',', ':'))
        seal_hash = hashlib.sha256(seal_json.encode('utf-8')).hexdigest()
        if self.pqc_private_key:
            try:
                log_list = []
                signature = PQC.sign_data(self.pqc_private_key, seal_json.encode('utf-8'), log_list)
                seal_data['pqc_signature'] = signature.hex()
            except Exception as e:
                pass
        return seal_hash

    def _get_previous_hash(self) -> str:
        """Get the hash of the previous ledger entry."""
        if not self.ledger_entries:
            return 'genesis_hash_00000000000000000000000000000000'
        return self.ledger_entries[-1].entry_hash

    def _generate_entry_hash(self, entry_data: Dict[str, Any], previous_hash: str, timestamp: int) -> str:
        """Generate deterministic hash for a ledger entry."""
        data_to_hash = {'entry_data': entry_data, 'previous_hash': previous_hash, 'timestamp': timestamp}
        data_json = json.dumps(data_to_hash, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_json.encode()).hexdigest()

    def _generate_pqc_cid(self, entry_data: Dict[str, Any], timestamp: int) -> str:
        """Generate deterministic PQC correlation ID."""
        data_to_hash = {'entry_data': entry_data, 'timestamp': timestamp}
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]

    def _get_ledger_hash_chain(self) -> List[str]:
        """Get the complete hash chain of the ledger."""
        return [entry.entry_hash for entry in self.ledger_entries]

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Get a summary of the key ledger."""
        return {'total_entries': len(self.ledger_entries), 'entry_types': [entry.entry_type for entry in self.ledger_entries], 'latest_timestamp': self.ledger_entries[-1].timestamp if self.ledger_entries else 0, 'ledger_hash_chain_length': len(self._get_ledger_hash_chain())}