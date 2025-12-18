"""
PQC_Audit.py - Phase-3 Module 2.3
PQC Audit Hash Generation and Log Export

Zero-Simulation Compliant, Deterministic Audit Trail
"""
import json
import hashlib
from typing import Any, Dict, List

class PQC_Audit:
    """
    Provides deterministic audit hash generation and log export functionality.
    Ensures replayable, verifiable audit trails for all PQC operations.
    """

    @staticmethod
    def get_pqc_audit_hash(log_list: List[Dict[str, Any]]) -> str:
        """
        Generate deterministic SHA3-512 hash of a given log list.
        Uses canonical serialization to ensure cross-node consistency.
        
        Args:
            log_list: List of log entries to hash
            
        Returns:
            SHA3-512 hash as hex string
            
        Raises:
            TypeError: If log entries contain non-serializable objects
        """
        from .CanonicalSerializer import CanonicalSerializer
        canonical_entries = []
        for entry in sorted(log_list):
            try:
                canonical_entries.append(CanonicalSerializer.canonicalize_for_sign(entry))
            except TypeError as e:
                raise TypeError(f'Non-deterministic type in audit log: {e}')
        serialized_log = json.dumps(canonical_entries, separators=(',', ':'), ensure_ascii=False)
        return hashlib.sha3_512(serialized_log.encode('utf-8')).hexdigest()

    @staticmethod
    def export_log(log_list: List[Dict[str, Any]], path: str) -> None:
        """
        Export the provided log list to a JSON file with canonical formatting.
        
        Args:
            log_list: List of log entries to export
            path: File path for export
        """
        from .CanonicalSerializer import CanonicalSerializer
        canonical_log = []
        for entry in sorted(log_list):
            canonical_log.append(json.loads(CanonicalSerializer.canonicalize_for_sign(entry)))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(canonical_log, f, indent=2, ensure_ascii=False)
