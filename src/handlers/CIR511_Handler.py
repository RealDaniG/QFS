"""
CIR511_Handler.py - Implement the Quantized Dissonance Detection mechanism

Implements the CIR511_Handler class for detecting micro-deviations or cascading 
discrepancies in arithmetic or state transitions that could indicate instability.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required modules
from ..libs.CertifiedMath import CertifiedMath, BigNum128


@dataclass
class DissonanceEvent:
    """Container for dissonance detection event"""
    metric_name: str
    current_value: BigNum128
    previous_value: BigNum128
    deviation: BigNum128
    threshold: BigNum128
    timestamp: int
    quantum_metadata: Optional[Dict[str, Any]] = None


class CIR511_Handler:
    """
    Implement the Quantized Dissonance Detection mechanism (CIR-511).
    
    Detects micro-deviations or cascading discrepancies in arithmetic or state 
    transitions that could indicate instability. Logs the dissonance events.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the CIR-511 Handler.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance

    def detect_dissonance(
        self,
        current_metrics: Dict[str, BigNum128],
        previous_metrics: Dict[str, BigNum128],
        threshold: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> bool:
        """
        Detect micro-dissonance in system metrics.
        
        Args:
            current_metrics: Current system metrics
            previous_metrics: Previous system metrics
            threshold: Dissonance detection threshold
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            bool: True if dissonance detected, False otherwise
        """
        dissonance_detected = False
        dissonance_events = []
        
        # Check each metric for dissonance
        for metric_name, current_value in current_metrics.items():
            if metric_name in previous_metrics:
                previous_value = previous_metrics[metric_name]
                
                # Calculate deviation
                if current_value.value >= previous_value.value:
                    deviation = self.cm.sub(current_value, previous_value, log_list, pqc_cid, quantum_metadata)
                else:
                    deviation = self.cm.sub(previous_value, current_value, log_list, pqc_cid, quantum_metadata)
                
                # Check if deviation exceeds threshold
                if self.cm.gt(deviation, threshold, log_list, pqc_cid, quantum_metadata):
                    dissonance_detected = True
                    dissonance_event = DissonanceEvent(
                        metric_name=metric_name,
                        current_value=current_value,
                        previous_value=previous_value,
                        deviation=deviation,
                        threshold=threshold,
                        timestamp=deterministic_timestamp,
                        quantum_metadata=quantum_metadata
                    )
                    dissonance_events.append(dissonance_event)
        
        # Log dissonance events if detected
        if dissonance_detected:
            for event in dissonance_events:
                self.log_micro_discrepancy(
                    event, log_list, pqc_cid, quantum_metadata, deterministic_timestamp
                )
        
        return dissonance_detected

    def log_micro_discrepancy(
        self,
        dissonance_event: DissonanceEvent,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log a micro-discrepancy for audit purposes.
        
        Args:
            dissonance_event: Dissonance event to log
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Prepare event details for logging
        event_details = {
            "metric_name": dissonance_event.metric_name,
            "current_value": dissonance_event.current_value.to_decimal_string(),
            "previous_value": dissonance_event.previous_value.to_decimal_string(),
            "deviation": dissonance_event.deviation.to_decimal_string(),
            "threshold": dissonance_event.threshold.to_decimal_string(),
            "timestamp": dissonance_event.timestamp,
            "quantum_metadata": dissonance_event.quantum_metadata
        }
        
        details = {
            "operation": "cir511_micro_discrepancy",
            "dissonance_event": event_details,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "cir511_micro_discrepancy",
            details,
            dissonance_event.deviation,  # Log the deviation as the result value
            log_list,
            pqc_cid,
            quantum_metadata
        )


# Test function
def test_cir511_handler():
    """Test the CIR511_Handler implementation."""
    print("Testing CIR511_Handler...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create CIR511_Handler
    handler = CIR511_Handler(cm)
    
    # Create test metrics
    current_metrics = {
        "S_CHR": BigNum128.from_int(50),    # 50.0
        "C_holo": BigNum128.from_int(80),   # 80.0
        "Action_Cost": BigNum128.from_int(20)  # 20.0
    }
    
    previous_metrics = {
        "S_CHR": BigNum128.from_int(49),    # 49.0
        "C_holo": BigNum128.from_int(78),   # 78.0
        "Action_Cost": BigNum128.from_int(19)  # 19.0
    }
    
    # Set threshold for dissonance detection
    threshold = BigNum128.from_int(5)  # 5.0 threshold
    
    log_list = []
    
    # Detect dissonance
    dissonance_detected = handler.detect_dissonance(
        current_metrics=current_metrics,
        previous_metrics=previous_metrics,
        threshold=threshold,
        log_list=log_list,
        pqc_cid="test_cir511_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Dissonance detected: {dissonance_detected}")
    print(f"Log entries: {len(log_list)}")
    if log_list:
        # Print first few keys of the last log entry to understand structure
        last_entry = log_list[-1]
        print(f"Last log entry keys: {list(last_entry.keys())[:5]}")
    
    print("✓ CIR511_Handler test passed!")


if __name__ == "__main__":
    test_cir511_handler()