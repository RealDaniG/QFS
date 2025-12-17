"""
AntiTamper.py - Detect runtime tampering with memory/code

Implements the AntiTamper class for calculating checksums/hashes of critical
code sections or data structures at known points and comparing them to detect
unexpected process changes.
"""

import json
import hashlib

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required modules
from ..libs.CertifiedMath import CertifiedMath, BigNum128
from .CIR412_Handler import CIR412_Handler, TamperEvidence
from .CIR302_Handler import CIR302_Handler


@dataclass
class IntegrityCheckResult:
    """Result of an integrity check"""

    section_name: str
    expected_hash: str
    actual_hash: str
    is_valid: bool
    timestamp: BigNum128  # Changed from int to BigNum128
    quantum_metadata: Optional[Dict[str, Any]] = None


class AntiTamper:
    """
    Detect runtime tampering with memory/code.

    Calculates checksums/hashes of critical code sections or data structures
    at known points and compares them. Monitors for unexpected process changes
    and interfaces with CIR302_Handler for fault classification and CIR412_Handler
    for anti-simulation enforcement.
    """

    def __init__(
        self,
        cm_instance: CertifiedMath,
        cir412_handler: CIR412_Handler,
        cir302_handler: CIR302_Handler,
    ):
        """
        Initialize the Anti-Tamper system.

        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
            cir412_handler: CIR412_Handler instance for anti-simulation enforcement
            cir302_handler: CIR302_Handler instance for fault classification
        """
        self.cm = cm_instance
        self.cir412_handler = cir412_handler
        self.cir302_handler = cir302_handler  # Added CIR302 handler
        self.reference_hashes: Dict[str, str] = {}

    def check_memory_integrity(
        self,
        section_name: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bool:
        """
        Check memory integrity for a specific section.

        Args:
            section_name: Name of the memory section to check
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            bool: True if memory integrity check passes, False otherwise
        """
        # Get reference hash for this section
        reference_hash = self.reference_hashes.get(section_name)
        if not reference_hash:
            # No reference hash available, cannot perform check
            return True

        # Calculate actual hash of the memory section
        actual_hash = self._calculate_memory_hash(
            section_name, log_list, pqc_cid, quantum_metadata
        )

        is_valid = actual_hash == reference_hash

        # Create integrity check result
        result = IntegrityCheckResult(
            section_name=section_name,
            expected_hash=reference_hash,
            actual_hash=actual_hash,
            is_valid=is_valid,
            timestamp=BigNum128.from_int(
                deterministic_timestamp
            ),  # Changed to BigNum128
            quantum_metadata=quantum_metadata,
        )

        # Log the integrity check
        self._log_integrity_check(
            result, log_list, pqc_cid, quantum_metadata, deterministic_timestamp
        )

        # Log success if valid
        if is_valid:
            self.cm._log_operation(
                "antitamper_pass",
                {"section": section_name},
                BigNum128.from_int(1),
                log_list,
                pqc_cid,
                quantum_metadata,
            )

        # If integrity check fails, first classify with CIR-302, then trigger CIR412
        if not is_valid:
            # Memory integrity violation detected - first classify with CIR-302
            self.cir302_handler.handle_violation(
                "memory_integrity_violation",
                f"Memory integrity violation for section '{section_name}'. Expected: {reference_hash}, Actual: {actual_hash}",
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp,
            )

            # Then enforce with CIR-412
            tamper_evidence = TamperEvidence(
                error_type="memory_integrity_violation",
                error_details=f"Memory integrity violation for section '{section_name}'. Expected: {reference_hash}, Actual: {actual_hash}",
                timestamp=deterministic_timestamp,
                quantum_metadata=quantum_metadata,
            )

            self.cir412_handler.trigger_halt(
                error_details=f"Memory integrity violation for section '{section_name}'",
                tamper_evidence=tamper_evidence,
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
            )

        return is_valid

    def check_code_hash(
        self,
        section_name: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bool:
        """
        Check code hash integrity for a specific section.

        Args:
            section_name: Name of the code section to check
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            bool: True if code hash check passes, False otherwise
        """
        # Get reference hash for this section
        reference_hash = self.reference_hashes.get(section_name)
        if not reference_hash:
            # No reference hash available, cannot perform check
            return True

        # Calculate actual hash of the code section
        actual_hash = self._calculate_code_hash(
            section_name, log_list, pqc_cid, quantum_metadata
        )

        is_valid = actual_hash == reference_hash

        # Create integrity check result
        result = IntegrityCheckResult(
            section_name=section_name,
            expected_hash=reference_hash,
            actual_hash=actual_hash,
            is_valid=is_valid,
            timestamp=BigNum128.from_int(
                deterministic_timestamp
            ),  # Changed to BigNum128
            quantum_metadata=quantum_metadata,
        )

        # Log the integrity check
        self._log_integrity_check(
            result, log_list, pqc_cid, quantum_metadata, deterministic_timestamp
        )

        # Log success if valid
        if is_valid:
            self.cm._log_operation(
                "antitamper_pass",
                {"section": section_name},
                BigNum128.from_int(1),
                log_list,
                pqc_cid,
                quantum_metadata,
            )

        # If integrity check fails, first classify with CIR-302, then trigger CIR412
        if not is_valid:
            # Code hash mismatch detected - first classify with CIR-302
            self.cir302_handler.handle_violation(
                "code_hash_mismatch",
                f"Code hash mismatch for section '{section_name}'. Expected: {reference_hash}, Actual: {actual_hash}",
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp,
            )

            # Then enforce with CIR-412
            tamper_evidence = TamperEvidence(
                error_type="code_hash_mismatch",
                error_details=f"Code hash mismatch for section '{section_name}'. Expected: {reference_hash}, Actual: {actual_hash}",
                timestamp=deterministic_timestamp,
                quantum_metadata=quantum_metadata,
            )

            self.cir412_handler.trigger_halt(
                error_details=f"Code hash mismatch for section '{section_name}'",
                tamper_evidence=tamper_evidence,
                log_list=log_list,
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata,
                deterministic_timestamp=deterministic_timestamp,
            )

        return is_valid

    def runtime_watchdog(self):
        """
        Runtime watchdog to monitor for unexpected process changes.

        In a real implementation, this would run periodically to check system integrity.
        For now, this is a placeholder for the conceptual watchdog mechanism.
        """
        # This would typically be implemented as a background thread or periodic check
        # that monitors various system aspects for tampering
        pass

    def set_reference_hash(self, section_name: str, hash_value: str):
        """
        Set reference hash for a specific section.

        Args:
            section_name: Name of the section
            hash_value: Reference hash value
        """
        self.reference_hashes[section_name] = hash_value

    def _load_snapshot(self, section_name: str) -> bytes:
        """
        Load deterministic snapshot from canonical path.

        Args:
            section_name: Name of the section

        Returns:
            bytes: Snapshot data
        """
        # QFS V13: No system-dependent paths. Use fixed, relative path.
        path = f"/qfs_snapshots/{section_name}.bin"
        # In a real implementation, this would load from a canonical path
        # For now, we'll simulate with deterministic data
        return f"snapshot_data_{section_name}".encode("utf-8")

    def _calculate_memory_hash(
        self,
        section_name: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Calculate hash of a memory section.

        Args:
            section_name: Name of the memory section
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata

        Returns:
            str: Calculated hash as hexadecimal string
        """
        # Calculate the actual hash of memory snapshot
        data = self._load_snapshot(section_name)
        return hashlib.sha256(data).hexdigest()

    def _calculate_code_hash(
        self,
        section_name: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Calculate hash of a code section.

        Args:
            section_name: Name of the code section
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata

        Returns:
            str: Calculated hash as hexadecimal string
        """
        # Calculate the actual hash of code snapshot
        data = self._load_snapshot(section_name)
        return hashlib.sha256(data).hexdigest()

    def _log_integrity_check(
        self,
        result: IntegrityCheckResult,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the integrity check for audit purposes.

        Args:
            result: Integrity check result
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Convert all values to strings for canonical logging
        converted_inputs = {
            "section": str(result.section_name),
            "expected": str(result.expected_hash),
            "actual": str(result.actual_hash),
            "valid": str(result.is_valid),  # bool → string
            "timestamp": result.timestamp.to_decimal_string(),  # BigNum128 string
        }

        self.cm._log_operation(
            "antitamper_integrity_check",
            converted_inputs,
            BigNum128.from_int(int(result.is_valid)),  # result as 0/1
            log_list,
            pqc_cid,
            quantum_metadata,
        )
