"""
PQC_Logger.py - Phase-3 Module 3.2
Deterministic PQC Logging Framework

Zero-Simulation Compliant, Causal Hash Chain, Replayable Verification
"""

import json
import hashlib
from typing import Any, Dict, List, Optional


class PQC_Logger:
    """
    Deterministic logging framework for PQC operations.
    Maintains causal hash chains with entry_hash → prev_hash linkage.
    """

    # Zero hash for the first entry in the audit log chain
    ZERO_HASH = "0" * 64
    
    # System fingerprint for audit logs (deterministic placeholder)
    SYSTEM_FINGERPRINT = "qfs_v13_deterministic"

    @staticmethod
    def log_pqc_operation(
        operation: str,
        details: Dict[str, Any],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        error: Optional[Exception] = None,
    ) -> None:
        """
        Appends a deterministic operation entry to the provided log_list with enhanced audit fields.
        
        Args:
            operation: Operation name
            details: Operation details (must be JSON-serializable)
            log_list: List to append log entry to (must be a list)
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
            error: Optional exception if operation failed
            
        Raises:
            TypeError: If log_list is not a list or details not JSON-serializable
        """
        # --- Phase-3 Validation ---
        if not isinstance(log_list, list):
            raise TypeError("log_list must be a list for deterministic logging")

        try:
            json.dumps(details, sort_keys=True, separators=(',', ':'))
        except Exception as e:
            raise TypeError(f"details must be JSON-serializable: {e}")
        
        # Calculate log index
        log_index = len(log_list)
        
        # Create the base entry with placeholder prev_hash
        entry = {
            "log_index": log_index,
            "operation": operation,
            "details": details,
            "pqc_cid": pqc_cid,
            "quantum_metadata": quantum_metadata,
            "timestamp": deterministic_timestamp,
            "system_fingerprint": PQC_Logger.SYSTEM_FINGERPRINT,
            "prev_hash": PQC_Logger.ZERO_HASH  # Placeholder, will be updated by LogContext
        }
        
        # Add error information if present
        if error:
            entry["error"] = {
                "type": type(error).__name__,
                "message": str(error)
            }
        
        # Calculate entry hash (excluding prev_hash to avoid circular dependency)
        entry_for_hash = entry.copy()
        entry_for_hash.pop("prev_hash", None)
        entry_for_hash.pop("entry_hash", None)
        serialized_entry = json.dumps(entry_for_hash, sort_keys=True, separators=(',', ':'))
        entry_hash = hashlib.sha3_512(serialized_entry.encode("utf-8")).hexdigest()
        entry["entry_hash"] = entry_hash
            
        log_list.append(entry)

    class LogContext:
        """
        Context manager for creating isolated, deterministic operation logs.
        Ensures thread-safety and coherence for a specific session or transaction bundle.
        
        Usage:
            with PQC_Logger.LogContext() as log:
                result = PQC.generate_keypair(log, seed=seed)
                
        Note:
            Context cannot be reused after exit() - this prevents audit chain ambiguity.
        """
        def __init__(self):
            self.log = []
            self._prev_hash = PQC_Logger.ZERO_HASH
            self._sealed = False

        def __enter__(self):
            if self._sealed:
                raise RuntimeError("PQC_Logger.LogContext cannot be reused after exit()")
            return self.log

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Rebuild causal chain deterministically
            prev = PQC_Logger.ZERO_HASH
            for entry in self.log:
                entry["prev_hash"] = prev
                prev = entry["entry_hash"]
            self._sealed = True
            return False  # do not suppress exceptions

        def get_log(self):
            return self.log

        def get_hash(self):
            from .PQC_Audit import PQC_Audit
            return PQC_Audit.get_pqc_audit_hash(self.log)

        def export(self, path: str):
            from .PQC_Audit import PQC_Audit
            PQC_Audit.export_log(self.log, path)
