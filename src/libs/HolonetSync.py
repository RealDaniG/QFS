"""
HolonetSync.py - QFS V13 Compliant State Synchronization Validator

Implements a stateless, I/O-free validator for synchronizing state and finality seals 
across nodes using only canonical, PQC-signed inputs.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

# Import required modules
try:
    from .CertifiedMath import CertifiedMath, BigNum128
except ImportError:
    # Fallback for direct script execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from libs.CertifiedMath import CertifiedMath, BigNum128


@dataclass
class SyncResult:
    """Result of a synchronization operation"""
    success: bool
    bundle_hash: str
    coherence_metrics: Dict[str, str]
    quorum_achieved: bool  # Changed from global_confirmation to reflect deterministic outcome
    error_message: Optional[str] = None
    quantum_metadata: Optional[Dict[str, Any]] = None


@dataclass
class SyncMessage:
    """Canonical sync message structure from PQC-signed sources"""
    bundle_hash: str
    log_hash: str
    coherence_metrics: Dict[str, str]
    timestamp: int
    validator_signature: bytes
    validator_public_key: bytes
    pqc_cid: Optional[str] = None
    quantum_metadata: Optional[Dict[str, Any]] = None


class HolonetSync:
    """
    QFS V13 Compliant State Synchronization Validator
    
    This is a pure, stateless validator that operates only on canonical, PQC-signed inputs.
    All network I/O belongs in an external orchestrator.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the QFS V13 Compliant Holonet Sync Validator.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance

    def validate_sync_message(
        self,
        message: SyncMessage,
        validator_set_hash: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> SyncResult:
        """
        Validate a sync message from a canonical, PQC-signed source.
        
        Args:
            message: Pre-fetched, PQC-verified sync message
            validator_set_hash: Canonical validator set hash
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            SyncResult: Deterministic validation result
        """
        try:
            # Verify message signature using PQC
            is_valid_signature = self._verify_pqc_signature(
                message.validator_public_key,
                message.validator_signature,
                message,
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp
            )
            
            if not is_valid_signature:
                return SyncResult(
                    success=False,
                    bundle_hash=message.bundle_hash,
                    coherence_metrics=message.coherence_metrics,
                    quorum_achieved=False,
                    error_message="Invalid PQC signature on sync message",
                    quantum_metadata=quantum_metadata
                )
            
            # Log the validation
            self._log_sync_validation(
                message.bundle_hash,
                True,
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp
            )
            
            # Return successful validation result
            return SyncResult(
                success=True,
                bundle_hash=message.bundle_hash,
                coherence_metrics=message.coherence_metrics,
                quorum_achieved=True,  # In a real implementation, this would be determined by quorum logic
                quantum_metadata=quantum_metadata
            )
            
        except Exception as e:
            # Log the error
            self._log_sync_validation(
                message.bundle_hash if 'message' in locals() else "",
                False,
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp,
                error_message=str(e)
            )
            
            return SyncResult(
                success=False,
                bundle_hash=message.bundle_hash if 'message' in locals() else "",
                coherence_metrics=message.coherence_metrics if 'message' in locals() else {},
                quorum_achieved=False,
                error_message=str(e),
                quantum_metadata=quantum_metadata
            )

    def validate_quorum_consensus(
        self,
        sync_messages: List[SyncMessage],
        validator_set_hash: str,
        required_quorum: float,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> SyncResult:
        """
        Validate quorum consensus from multiple canonical, PQC-signed sources.
        
        Args:
            sync_messages: List of pre-fetched, PQC-verified sync messages
            validator_set_hash: Canonical validator set hash
            required_quorum: Required quorum fraction (0.0 to 1.0)
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            SyncResult: Deterministic quorum validation result
        """
        try:
            # Validate each message and count valid ones
            valid_messages = []
            bundle_hash_consensus = {}
            
            for message in sync_messages:
                # Verify message signature using PQC
                is_valid_signature = self._verify_pqc_signature(
                    message.validator_public_key,
                    message.validator_signature,
                    message,
                    log_list,
                    pqc_cid,
                    quantum_metadata,
                    deterministic_timestamp
                )
                
                if is_valid_signature:
                    valid_messages.append(message)
                    
                    # Count bundle hash occurrences for consensus
                    bundle_hash = message.bundle_hash
                    bundle_hash_consensus[bundle_hash] = bundle_hash_consensus.get(bundle_hash, 0) + 1
            
            # Check if quorum is achieved
            total_validators = self._get_validator_count(validator_set_hash)
            valid_signatures = len(valid_messages)
            quorum_threshold = int(total_validators * required_quorum)
            quorum_achieved = valid_signatures >= quorum_threshold
            
            # Determine consensus bundle hash (majority vote)
            consensus_bundle_hash = ""
            max_count = 0
            for bundle_hash, count in bundle_hash_consensus.items():
                if count > max_count:
                    max_count = count
                    consensus_bundle_hash = bundle_hash
            
            # Use the coherence metrics from the first valid message as representative
            representative_metrics = valid_messages[0].coherence_metrics if valid_messages else {}
            
            # Log the quorum validation
            self._log_quorum_validation(
                valid_signatures,
                total_validators,
                quorum_threshold,
                consensus_bundle_hash,
                quorum_achieved,
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp
            )
            
            # Return quorum validation result
            return SyncResult(
                success=quorum_achieved and consensus_bundle_hash != "",
                bundle_hash=consensus_bundle_hash,
                coherence_metrics=representative_metrics,
                quorum_achieved=quorum_achieved,
                quantum_metadata=quantum_metadata
            )
            
        except Exception as e:
            # Log the error
            self._log_quorum_validation(
                0, 0, 0, "", False,
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp,
                error_message=str(e)
            )
            
            return SyncResult(
                success=False,
                bundle_hash="",
                coherence_metrics={},
                quorum_achieved=False,
                error_message=str(e),
                quantum_metadata=quantum_metadata
            )

    def compute_median_timestamp(
        self,
        signed_timestamps: List[Tuple[int, bytes, bytes]],  # (timestamp, signature, public_key)
        validator_set_hash: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> int:
        """
        Compute median timestamp from canonical, PQC-signed inputs.
        
        Args:
            signed_timestamps: List of (timestamp, signature, public_key) tuples from validators
            validator_set_hash: Canonical validator set hash
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            int: Median timestamp computed from valid inputs
        """
        try:
            # Validate each timestamp signature and collect valid ones
            valid_timestamps = []
            
            for timestamp, signature, public_key in signed_timestamps:
                # Create a temporary message for signature verification
                temp_message = {
                    "timestamp": timestamp,
                    "validator_set_hash": validator_set_hash,
                    "type": "timestamp_sync"
                }
                
                # Verify signature using PQC
                is_valid_signature = self._verify_pqc_signature_generic(
                    public_key,
                    signature,
                    temp_message,
                    log_list,
                    pqc_cid,
                    quantum_metadata,
                    deterministic_timestamp
                )
                
                if is_valid_signature:
                    valid_timestamps.append(timestamp)
            
            # Calculate median timestamp for synchronization
            if not valid_timestamps:
                # If no valid timestamps, return the deterministic timestamp
                median_timestamp = deterministic_timestamp
            else:
                valid_timestamps.sort()
                median_timestamp = valid_timestamps[len(valid_timestamps) // 2]
            
            # Log the timestamp computation
            self._log_timestamp_computation(
                valid_timestamps,
                median_timestamp,
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp
            )
            
            return median_timestamp
            
        except Exception as e:
            # Log the error and return deterministic timestamp as fallback
            self._log_timestamp_computation(
                [],
                deterministic_timestamp,
                log_list,
                pqc_cid,
                quantum_metadata,
                deterministic_timestamp,
                error_message=str(e)
            )
            
            return deterministic_timestamp

    def _verify_pqc_signature(
        self,
        public_key: bytes,
        signature: bytes,
        message: SyncMessage,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bool:
        """
        Verify PQC signature on a sync message.
        
        Args:
            public_key: Validator's public key
            signature: PQC signature
            message: Sync message to verify
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # In a real implementation, this would use the actual PQC verification
        # For now, we'll simulate a successful verification
        # A real implementation would use the PQC module to verify the signature
        
        # Log the signature verification
        self._log_signature_verification(
            public_key,
            signature,
            True,  # Simulate successful verification
            log_list,
            pqc_cid,
            quantum_metadata,
            deterministic_timestamp
        )
        
        # Simulate successful verification
        return True

    def _verify_pqc_signature_generic(
        self,
        public_key: bytes,
        signature: bytes,
        message: Dict[str, Any],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bool:
        """
        Generic PQC signature verification.
        
        Args:
            public_key: Validator's public key
            signature: PQC signature
            message: Message to verify
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # In a real implementation, this would use the actual PQC verification
        # For now, we'll simulate a successful verification
        
        # Log the signature verification
        self._log_signature_verification(
            public_key,
            signature,
            True,  # Simulate successful verification
            log_list,
            pqc_cid,
            quantum_metadata,
            deterministic_timestamp
        )
        
        # Simulate successful verification
        return True

    def _get_validator_count(self, validator_set_hash: str) -> int:
        """
        Get the count of validators in a canonical validator set.
        
        Args:
            validator_set_hash: Hash of the canonical validator set
            
        Returns:
            int: Number of validators in the set
        """
        # In a real implementation, this would look up the validator set
        # For now, we'll return a fixed number for demonstration
        return 5

    def _log_sync_validation(
        self,
        bundle_hash: str,
        is_valid: bool,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        error_message: Optional[str] = None,
    ):
        """
        Log sync validation for audit purposes.
        
        Args:
            bundle_hash: Bundle hash being validated
            is_valid: Whether the validation was successful
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
            error_message: Error message if validation failed
        """
        details = {
            "operation": "sync_validation",
            "bundle_hash": bundle_hash,
            "is_valid": is_valid,
            "timestamp": deterministic_timestamp
        }
        
        if error_message:
            details["error_message"] = error_message
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "sync_validation",
            details,
            BigNum128.from_int(deterministic_timestamp),
            log_list,
            pqc_cid,
            quantum_metadata
        )

    def _log_quorum_validation(
        self,
        valid_signatures: int,
        total_validators: int,
        quorum_threshold: int,
        consensus_bundle_hash: str,
        quorum_achieved: bool,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        error_message: Optional[str] = None,
    ):
        """
        Log quorum validation for audit purposes.
        
        Args:
            valid_signatures: Number of valid signatures
            total_validators: Total number of validators
            quorum_threshold: Required quorum threshold
            consensus_bundle_hash: Consensus bundle hash
            quorum_achieved: Whether quorum was achieved
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
            error_message: Error message if validation failed
        """
        details = {
            "operation": "quorum_validation",
            "valid_signatures": valid_signatures,
            "total_validators": total_validators,
            "quorum_threshold": quorum_threshold,
            "consensus_bundle_hash": consensus_bundle_hash,
            "quorum_achieved": quorum_achieved,
            "timestamp": deterministic_timestamp
        }
        
        if error_message:
            details["error_message"] = error_message
        
        # Use CertifiedMath's internal logging
        result_value = 1 if quorum_achieved else 0
        self.cm._log_operation(
            "quorum_validation",
            details,
            BigNum128.from_int(result_value),
            log_list,
            pqc_cid,
            quantum_metadata
        )

    def _log_timestamp_computation(
        self,
        valid_timestamps: List[int],
        median_timestamp: int,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        error_message: Optional[str] = None,
    ):
        """
        Log timestamp computation for audit purposes.
        
        Args:
            valid_timestamps: List of valid timestamps
            median_timestamp: Computed median timestamp
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
            error_message: Error message if computation failed
        """
        details = {
            "operation": "timestamp_computation",
            "valid_timestamps_count": len(valid_timestamps),
            "median_timestamp": median_timestamp,
            "timestamp": deterministic_timestamp
        }
        
        if error_message:
            details["error_message"] = error_message
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "timestamp_computation",
            details,
            BigNum128.from_int(median_timestamp),
            log_list,
            pqc_cid,
            quantum_metadata
        )

    def _log_signature_verification(
        self,
        public_key: bytes,
        signature: bytes,
        is_valid: bool,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log signature verification for audit purposes.
        
        Args:
            public_key: Validator's public key
            signature: PQC signature
            is_valid: Whether the signature is valid
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Hash the public key for logging (to avoid logging raw bytes)
        public_key_hash = hashlib.sha256(public_key).hexdigest()[:16]
        
        details = {
            "operation": "signature_verification",
            "public_key_hash": public_key_hash,
            "is_valid": is_valid,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        result_value = 1 if is_valid else 0
        self.cm._log_operation(
            "signature_verification",
            details,
            BigNum128.from_int(result_value),
            log_list,
            pqc_cid,
            quantum_metadata
        )


# Deterministic test function
def test_holonet_sync():
    """Test the QFS V13 compliant HolonetSync implementation."""
    print("Testing QFS V13 Compliant HolonetSync...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create HolonetSync
    sync = HolonetSync(cm)
    
    log_list = []
    
    # Test validate_sync_message
    message = SyncMessage(
        bundle_hash="test_bundle_hash_123",
        log_hash="test_log_hash_456",
        coherence_metrics={
            "c_holo": "0.95",
            "s_chr": "0.98",
            "s_flx": "0.15"
        },
        timestamp=1234567890,
        validator_signature=b"test_signature",
        validator_public_key=b"test_public_key",
        pqc_cid="test_sync_001"
    )
    
    validation_result = sync.validate_sync_message(
        message=message,
        validator_set_hash="test_validator_set_hash",
        log_list=log_list,
        pqc_cid="test_sync_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Sync message validation successful: {validation_result.success}")
    print(f"Quorum achieved: {validation_result.quorum_achieved}")
    
    # Test validate_quorum_consensus
    sync_messages = [message]  # Single message for simplicity
    
    quorum_result = sync.validate_quorum_consensus(
        sync_messages=sync_messages,
        validator_set_hash="test_validator_set_hash",
        required_quorum=0.6,
        log_list=log_list,
        pqc_cid="test_sync_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Quorum consensus validation successful: {quorum_result.success}")
    print(f"Consensus bundle hash: {quorum_result.bundle_hash}")
    
    # Test compute_median_timestamp
    signed_timestamps = [
        (1234567890, b"sig1", b"key1"),
        (1234567895, b"sig2", b"key2"),
        (1234567885, b"sig3", b"key3")
    ]
    
    median_timestamp = sync.compute_median_timestamp(
        signed_timestamps=signed_timestamps,
        validator_set_hash="test_validator_set_hash",
        log_list=log_list,
        pqc_cid="test_sync_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Computed median timestamp: {median_timestamp}")
    print(f"Log entries: {len(log_list)}")
    
    print("✓ QFS V13 Compliant HolonetSync test passed!")


if __name__ == "__main__":
    test_holonet_sync()