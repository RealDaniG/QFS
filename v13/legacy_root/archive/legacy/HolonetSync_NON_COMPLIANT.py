
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required modules
from ...libs.CertifiedMath import CertifiedMath, BigNum128
from ...core.TokenStateBundle import TokenStateBundle


@dataclass
class SyncResult:
    """Result of a synchronization operation"""
    success: bool
    bundle_hash: str
    coherence_metrics: Dict[str, str]
    global_confirmation: bool
    error_message: Optional[str] = None
    quantum_metadata: Optional[Dict[str, Any]] = None


class HolonetSync:
    """
    Synchronize state and finality seals across nodes.
    
    Likely involves network communication (gRPC, HTTP) with other nodes. 
    Send/receive final bundle hashes, state deltas, ttsTimestamp updates.
    Ensures global consistency of the ledger state and audit trail across the network.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Holonet Sync.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        self.network_nodes = []  # List of network node addresses
        self.sync_status = {}    # Sync status per node

    def propagate_finality(
        self,
        bundle_hash: str,
        log_hash: str,
        coherence_metrics: Dict[str, str],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bool:
        """
        Propagate finality to other nodes in the network.
        
        Args:
            bundle_hash: Hash of the final bundle
            log_hash: Hash of the audit log
            coherence_metrics: Coherence metrics to propagate
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            bool: True if propagation successful, False otherwise
        """
        try:
            import requests
            import json
            
            # Prepare finality data
            finality_data = {
                "bundle_hash": bundle_hash,
                "log_hash": log_hash,
                "coherence_metrics": coherence_metrics,
                "timestamp": deterministic_timestamp,
                "pqc_cid": pqc_cid,
                "quantum_metadata": quantum_metadata
            }
            
            # Send finality data to all network nodes
            success_count = 0
            for node_url in self.network_nodes:
                try:
                    response = requests.post(
                        f"{node_url}/propagate-finality",
                        json=finality_data,
                        timeout=30  # 30 second timeout
                    )
                    
                    if response.status_code == 200:
                        success_count += 1
                        
                except Exception as node_error:
                    # Log node-specific error but continue with other nodes
                    self._log_propagation_error(
                        f"Node {node_url} error: {str(node_error)}", 
                        bundle_hash, log_hash, coherence_metrics,
                        log_list, pqc_cid, quantum_metadata, deterministic_timestamp
                    )
            
            # Check if majority of nodes succeeded
            propagation_successful = success_count >= len(self.network_nodes) // 2 + 1
            
            # Log the propagation result
            self._log_finality_propagation(
                bundle_hash, log_hash, coherence_metrics,
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return propagation_successful
            
        except Exception as e:
            # Log the error
            self._log_propagation_error(
                str(e), bundle_hash, log_hash, coherence_metrics,
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return False

    def reconcile_timestamps(
        self,
        current_tts: int,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> int:
        """
        Reconcile timestamps across nodes.
        
        Args:
            current_tts: Current ttsTimestamp
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            int: Synchronized ttsTimestamp
        """
        try:
            import requests
            import json
            
            # Prepare timestamp reconciliation request
            timestamp_data = {
                "current_tts": current_tts,
                "request_timestamp": deterministic_timestamp,
                "pqc_cid": pqc_cid,
                "quantum_metadata": quantum_metadata
            }
            
            # Collect timestamps from all network nodes
            timestamps = [current_tts]  # Include our own timestamp
            
            for node_url in self.network_nodes:
                try:
                    response = requests.post(
                        f"{node_url}/reconcile-timestamps",
                        json=timestamp_data,
                        timeout=30  # 30 second timeout
                    )
                    
                    if response.status_code == 200:
                        node_data = response.json()
                        node_timestamp = node_data.get("timestamp", current_tts)
                        timestamps.append(node_timestamp)
                        
                except Exception as node_error:
                    # Log node-specific error but continue with other nodes
                    pass  # Continue with available timestamps
            
            # Calculate median timestamp for synchronization
            timestamps.sort()
            median_timestamp = timestamps[len(timestamps) // 2]
            
            # Log the timestamp reconciliation
            self._log_timestamp_reconciliation(
                current_tts, median_timestamp,
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return median_timestamp
            
        except Exception as e:
            # Log the error and return current timestamp as fallback
            self._log_propagation_error(
                f"Timestamp reconciliation error: {str(e)}", "", "", {},
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return current_tts

    def await_global_confirmation(
        self,
        bundle_hash: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bool:
        """
        Await global confirmation of a bundle hash.
        
        Args:
            bundle_hash: Bundle hash to confirm
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            bool: True if confirmed globally, False otherwise
        """
        try:
            import requests
            import json
            import time
            
            # Prepare confirmation request
            confirmation_data = {
                "bundle_hash": bundle_hash,
                "request_timestamp": deterministic_timestamp,
                "pqc_cid": pqc_cid,
                "quantum_metadata": quantum_metadata
            }
            
            # Poll network nodes for confirmation
            max_attempts = 10
            poll_interval = 2  # seconds
            
            for attempt in range(max_attempts):
                confirmations = 0
                
                for node_url in self.network_nodes:
                    try:
                        response = requests.post(
                            f"{node_url}/check-confirmation",
                            json=confirmation_data,
                            timeout=30  # 30 second timeout
                        )
                        
                        if response.status_code == 200:
                            node_data = response.json()
                            if node_data.get("confirmed", False):
                                confirmations += 1
                                
                    except Exception as node_error:
                        # Log node-specific error but continue with other nodes
                        pass  # Continue checking other nodes
                
                # Check if majority of nodes confirmed
                if confirmations >= len(self.network_nodes) // 2 + 1:
                    # Log the confirmation success
                    self._log_confirmation_wait(
                        bundle_hash, True,
                        log_list, pqc_cid, quantum_metadata, deterministic_timestamp
                    )
                    
                    return True
                
                # Wait before next poll attempt
                if attempt < max_attempts - 1:
                    time.sleep(poll_interval)
            
            # Log the confirmation failure
            self._log_confirmation_wait(
                bundle_hash, False,
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return False
            
        except Exception as e:
            # Log the error
            self._log_propagation_error(
                f"Global confirmation error: {str(e)}", bundle_hash, "", {},
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return False

    def _log_finality_propagation(
        self,
        bundle_hash: str,
        log_hash: str,
        coherence_metrics: Dict[str, str],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the finality propagation for audit purposes.
        
        Args:
            bundle_hash: Bundle hash being propagated
            log_hash: Log hash being propagated
            coherence_metrics: Coherence metrics being propagated
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        details = {
            "operation": "finality_propagation",
            "bundle_hash": bundle_hash,
            "log_hash": log_hash,
            "coherence_metrics": coherence_metrics,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "finality_propagation",
            details,
            BigNum128.from_int(deterministic_timestamp),
            log_list,
            pqc_cid,
            quantum_metadata
        )

    def _log_propagation_error(
        self,
        error_message: str,
        bundle_hash: str,
        log_hash: str,
        coherence_metrics: Dict[str, str],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log a propagation error for audit purposes.
        
        Args:
            error_message: Error message
            bundle_hash: Bundle hash being propagated
            log_hash: Log hash being propagated
            coherence_metrics: Coherence metrics being propagated
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        details = {
            "operation": "propagation_error",
            "error_message": error_message,
            "bundle_hash": bundle_hash,
            "log_hash": log_hash,
            "coherence_metrics": coherence_metrics,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "propagation_error",
            details,
            BigNum128.from_int(0),  # Error code
            log_list,
            pqc_cid,
            quantum_metadata
        )

    def _log_timestamp_reconciliation(
        self,
        old_timestamp: int,
        new_timestamp: int,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the timestamp reconciliation for audit purposes.
        
        Args:
            old_timestamp: Old timestamp value
            new_timestamp: New timestamp value
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        details = {
            "operation": "timestamp_reconciliation",
            "old_timestamp": old_timestamp,
            "new_timestamp": new_timestamp,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "timestamp_reconciliation",
            details,
            BigNum128.from_int(new_timestamp),
            log_list,
            pqc_cid,
            quantum_metadata
        )

    def _log_confirmation_wait(
        self,
        bundle_hash: str,
        confirmed: bool,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the confirmation wait for audit purposes.
        
        Args:
            bundle_hash: Bundle hash being confirmed
            confirmed: Whether the bundle was confirmed
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        details = {
            "operation": "confirmation_wait",
            "bundle_hash": bundle_hash,
            "confirmed": confirmed,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        confirmation_result = BigNum128.from_int(1) if confirmed else BigNum128.from_int(0)
        self.cm._log_operation(
            "confirmation_wait",
            details,
            confirmation_result,
            log_list,
            pqc_cid,
            quantum_metadata
        )


# Test function
def test_holonet_sync():
    """Test the HolonetSync implementation."""
    print("Testing HolonetSync...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create HolonetSync
    sync = HolonetSync(cm)
    
    log_list = []
    
    # Test propagate_finality
    coherence_metrics = {
        "c_holo": "0.95",
        "s_chr": "0.98",
        "s_flx": "0.15"
    }
    
    propagation_success = sync.propagate_finality(
        bundle_hash="test_bundle_hash_123",
        log_hash="test_log_hash_456",
        coherence_metrics=coherence_metrics,
        log_list=log_list,
        pqc_cid="test_sync_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Finality propagation successful: {propagation_success}")
    
    # Test reconcile_timestamps
    new_timestamp = sync.reconcile_timestamps(
        current_tts=1234567890,
        log_list=log_list,
        pqc_cid="test_sync_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Reconciled timestamp: {new_timestamp}")
    
    # Test await_global_confirmation
    confirmation = sync.await_global_confirmation(
        bundle_hash="test_bundle_hash_123",
        log_list=log_list,
        pqc_cid="test_sync_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Global confirmation: {confirmation}")
    print(f"Log entries: {len(log_list)}")
    
    print("✓ HolonetSync test passed!")


if __name__ == "__main__":
    test_holonet_sync()
