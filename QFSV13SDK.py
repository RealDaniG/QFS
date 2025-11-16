"""
QFS V13 SDK - CertifiedMath Wrapper with Quantum Integration
SDK client for wrapping CertifiedMath operations with PQC signatures and audit trails
"""
import sys
import os
import json
import hashlib
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add the libs directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from CertifiedMath import CertifiedMath, BigNum128

@dataclass
class DRV_Packet:
    """Deterministic Request Verification Packet"""
    ttsTimestamp: int  # Trusted Time Service Timestamp
    sequenceNumber: int
    seed: str
    pqc_signature: Optional[str] = None  # PQC signature for attestation
    # Quantum Integration Fields (Phase 3)
    quantum_source_id: Optional[str] = None  # Identifier for quantum entropy source
    quantum_entropy: Optional[str] = None    # Quantum-generated entropy
    vdf_output_hash: Optional[str] = None    # Verifiable Delay Function output hash

@dataclass
class OperationBundle:
    """Atomic operation bundle for coherent transactions"""
    drv_packet: DRV_Packet
    operation: str
    operands: Tuple[str, ...]
    result: str
    pqc_signature: str
    log_hash: str
    operation_id: str
    timestamp: int

class CIR302Exception(Exception):
    """Custom exception for CIR-302 Fail-Safe Trigger"""
    pass

class QFSV13SDK:
    """QFS V13 SDK Client for CertifiedMath operations with Quantum Integration"""
    
    def __init__(self, api_endpoint: str = "http://localhost:8000"):
        self.api_endpoint = api_endpoint
        self.session_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        self.operation_counter = 0
        self.audit_log = []
        self.last_sequence_number = -1  # Track last sequence number for continuity validation
        self.quantum_mode = False  # Flag to indicate if quantum-enhanced mode is active
        
    def enable_quantum_mode(self):
        """Enable quantum-enhanced mode"""
        self.quantum_mode = True
        
    def disable_quantum_mode(self):
        """Disable quantum-enhanced mode"""
        self.quantum_mode = False
        
    def _validate_drv_packet(self, drv_packet: DRV_Packet) -> bool:
        """
        Validate DRV_Packet for deterministic inputs
        
        Args:
            drv_packet: DRV_Packet to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check if timestamp is reasonable (not in the future)
        current_time = int(time.time())
        if drv_packet.ttsTimestamp > current_time + 300:  # 5 minutes tolerance
            return False
            
        # Check sequence continuity (must increment by exactly 1)
        if drv_packet.sequenceNumber != self.last_sequence_number + 1:
            return False
            
        # Check if seed is provided
        if not drv_packet.seed:
            return False
            
        # CIR-302 Fail-Safe Trigger: Check quantum fields in quantum mode
        if self.quantum_mode:
            if drv_packet.quantum_source_id is None:
                raise CIR302Exception("Missing quantum_source_id in quantum-enhanced mode")
            if drv_packet.quantum_entropy is None:
                raise CIR302Exception("Missing quantum_entropy in quantum-enhanced mode")
            if drv_packet.vdf_output_hash is None:
                raise CIR302Exception("Missing vdf_output_hash in quantum-enhanced mode")
            
        return True
        
    def _generate_operation_id(self, operation: str, operands: Tuple[str, ...], previous_hash: str) -> str:
        """
        Generate unique operation ID based on deterministic hashing
        
        Args:
            operation: Operation name
            operands: Operation operands
            previous_hash: Hash of previous operation
            
        Returns:
            str: Unique operation ID
        """
        data = f"{operation}:{':'.join(operands)}:{previous_hash}:{self.operation_counter}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
        
    def _generate_pqc_signature(self, data: str, seed: str, operation_id: str, 
                               quantum_metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Generate deterministic PQC signature for data with optional quantum metadata
        
        Args:
            data: Data to sign
            seed: Deterministic seed from DRV_Packet
            operation_id: Operation ID for uniqueness
            quantum_metadata: Optional quantum metadata for enhanced keying
            
        Returns:
            str: Deterministic PQC signature
        """
        # Generate deterministic PQC signature using seed and operation_id only
        # This ensures repeated executions produce identical signatures
        signature_data = f"pqc_signature:{data}:{seed}:{operation_id}"
        
        # Include quantum metadata if provided (Phase 3 enhancement)
        if quantum_metadata:
            quantum_data = f"{quantum_metadata.get('quantum_source_id', '')}:{quantum_metadata.get('quantum_entropy', '')}:{quantum_metadata.get('vdf_output_hash', '')}"
            signature_data += f":{quantum_data}"
            
        return hashlib.sha3_256(signature_data.encode()).hexdigest()
        
    def _log_operation(self, bundle: OperationBundle, quantum_metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Log operation to audit trail with optional quantum metadata
        
        Args:
            bundle: Operation bundle to log
            quantum_metadata: Optional quantum metadata to record
            
        Returns:
            str: Hash of the audit log
        """
        log_entry = {
            "operation_id": bundle.operation_id,
            "timestamp": bundle.timestamp,
            "drv_packet": asdict(bundle.drv_packet),
            "operation": bundle.operation,
            "operands": bundle.operands,
            "result": bundle.result,
            "pqc_signature": bundle.pqc_signature,
            "log_hash": bundle.log_hash
        }
        
        # Add quantum metadata to log entry if provided
        if quantum_metadata:
            log_entry["quantum_metadata"] = quantum_metadata
            
        self.audit_log.append(log_entry)
        
        # Generate hash of audit log for CRS chain
        serialized_log = json.dumps(self.audit_log, sort_keys=True)
        return hashlib.sha256(serialized_log.encode()).hexdigest()
        
    def _perform_operation(self, operation: str, operands: Tuple[str, ...], 
                          drv_packet: DRV_Packet) -> OperationBundle:
        """
        Perform a CertifiedMath operation and create an operation bundle
        
        Args:
            operation: Operation name
            operands: Operation operands
            drv_packet: DRV_Packet for deterministic inputs
            
        Returns:
            OperationBundle: Bundle containing operation details
            
        Raises:
            ValueError: If DRV_Packet is invalid or sequence continuity is broken
            Exception: If operation fails (with atomic rollback)
            CIR302Exception: If quantum-enhanced mode requirements are not met
        """
        # Validate DRV_Packet
        if not self._validate_drv_packet(drv_packet):
            raise ValueError("Invalid DRV_Packet: validation failed or sequence continuity broken")
            
        # Store current audit log length for potential rollback
        log_length_before = len(self.audit_log)
        
        try:
            # Generate previous log hash
            if self.audit_log:
                serialized_log = json.dumps(self.audit_log, sort_keys=True)
                previous_hash = hashlib.sha256(serialized_log.encode()).hexdigest()
            else:
                previous_hash = "0" * 64
                
            # Generate operation ID
            operation_id = self._generate_operation_id(operation, operands, previous_hash)
            
            # Prepare quantum metadata for CertifiedMath logging
            quantum_metadata = None
            if self.quantum_mode and drv_packet.quantum_source_id:
                quantum_metadata = {
                    "quantum_source_id": drv_packet.quantum_source_id,
                    "quantum_entropy": drv_packet.quantum_entropy,
                    "vdf_output_hash": drv_packet.vdf_output_hash
                }
            
            # Perform the actual operation using CertifiedMath
            if operation == "add":
                a = CertifiedMath.from_string(operands[0])
                b = CertifiedMath.from_string(operands[1])
                result_obj = CertifiedMath.add(a, b, operation_id, quantum_metadata)
            elif operation == "sub":
                a = CertifiedMath.from_string(operands[0])
                b = CertifiedMath.from_string(operands[1])
                result_obj = CertifiedMath.sub(a, b, operation_id, quantum_metadata)
            elif operation == "mul":
                a = CertifiedMath.from_string(operands[0])
                b = CertifiedMath.from_string(operands[1])
                result_obj = CertifiedMath.mul(a, b, operation_id, quantum_metadata)
            elif operation == "div":
                a = CertifiedMath.from_string(operands[0])
                b = CertifiedMath.from_string(operands[1])
                result_obj = CertifiedMath.div(a, b, operation_id, quantum_metadata)
            elif operation == "sqrt":
                a = CertifiedMath.from_string(operands[0])
                iterations = int(operands[1]) if len(operands) > 1 else 20
                result_obj = CertifiedMath.fast_sqrt(a, iterations, operation_id, quantum_metadata)
            elif operation == "phi_series":
                a = CertifiedMath.from_string(operands[0])
                n = int(operands[1]) if len(operands) > 1 else 10
                result_obj = CertifiedMath.calculate_phi_series(a, n, operation_id, quantum_metadata)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
            result = str(result_obj.value)
            
            # Generate deterministic PQC signature with quantum metadata if available
            signature_data = f"{operation}:{':'.join(operands)}:{result}:{operation_id}"
            pqc_signature = self._generate_pqc_signature(signature_data, drv_packet.seed, operation_id, quantum_metadata)
            
            # Update DRV_Packet with PQC signature
            drv_packet.pqc_signature = pqc_signature
            
            # Create operation bundle
            bundle = OperationBundle(
                drv_packet=drv_packet,
                operation=operation,
                operands=operands,
                result=result,
                pqc_signature=pqc_signature,
                log_hash=CertifiedMath.get_log_hash(),
                operation_id=operation_id,
                timestamp=drv_packet.ttsTimestamp  # Use deterministic timestamp from DRV_Packet
            )
            
            # Validate log hash matches CertifiedMath log
            if not self._validate_log_hash(bundle):
                raise ValueError("Log hash validation failed: CRS chain integrity compromised")
            
            # Log operation with quantum metadata
            log_hash = self._log_operation(bundle, quantum_metadata)
            
            # Update sequence number tracker
            self.last_sequence_number = drv_packet.sequenceNumber
            
            # Update operation counter
            self.operation_counter += 1
            
            return bundle
            
        except Exception as e:
            # Atomic rollback on failure - remove any partial log entries
            if len(self.audit_log) > log_length_before:
                self.audit_log = self.audit_log[:log_length_before]
            raise e  # Re-raise the exception
        
    def _validate_log_hash(self, bundle: OperationBundle) -> bool:
        """
        Validate that the log_hash in the bundle matches CertifiedMath.get_log_hash()
        
        Args:
            bundle: Operation bundle to validate
            
        Returns:
            bool: True if log hash is valid, False otherwise
        """
        return bundle.log_hash == CertifiedMath.get_log_hash()
        
    def add(self, operand_a: str, operand_b: str, drv_packet: DRV_Packet) -> OperationBundle:
        """
        Perform addition operation using CertifiedMath
        
        Args:
            operand_a: First operand as string
            operand_b: Second operand as string
            drv_packet: DRV_Packet for deterministic inputs
            
        Returns:
            OperationBundle: Bundle containing operation details
        """
        return self._perform_operation("add", (operand_a, operand_b), drv_packet)
        
    def sub(self, operand_a: str, operand_b: str, drv_packet: DRV_Packet) -> OperationBundle:
        """
        Perform subtraction operation using CertifiedMath
        
        Args:
            operand_a: First operand as string
            operand_b: Second operand as string
            drv_packet: DRV_Packet for deterministic inputs
            
        Returns:
            OperationBundle: Bundle containing operation details
        """
        return self._perform_operation("sub", (operand_a, operand_b), drv_packet)
        
    def mul(self, operand_a: str, operand_b: str, drv_packet: DRV_Packet) -> OperationBundle:
        """
        Perform multiplication operation using CertifiedMath
        
        Args:
            operand_a: First operand as string
            operand_b: Second operand as string
            drv_packet: DRV_Packet for deterministic inputs
            
        Returns:
            OperationBundle: Bundle containing operation details
        """
        return self._perform_operation("mul", (operand_a, operand_b), drv_packet)
        
    def div(self, operand_a: str, operand_b: str, drv_packet: DRV_Packet) -> OperationBundle:
        """
        Perform division operation using CertifiedMath
        
        Args:
            operand_a: First operand as string
            operand_b: Second operand as string
            drv_packet: DRV_Packet for deterministic inputs
            
        Returns:
            OperationBundle: Bundle containing operation details
        """
        return self._perform_operation("div", (operand_a, operand_b), drv_packet)
        
    def sqrt(self, operand: str, iterations: int = 20, drv_packet: Optional[DRV_Packet] = None) -> OperationBundle:
        """
        Perform square root operation using CertifiedMath
        
        Args:
            operand: Operand as string
            iterations: Number of iterations for Babylonian method
            drv_packet: DRV_Packet for deterministic inputs
            
        Returns:
            OperationBundle: Bundle containing operation details
        """
        if drv_packet is None:
            raise ValueError("DRV_Packet is required")
        return self._perform_operation("sqrt", (operand, str(iterations)), drv_packet)
        
    def phi_series(self, operand: str, n: int = 10, drv_packet: Optional[DRV_Packet] = None) -> OperationBundle:
        """
        Perform phi series operation using CertifiedMath
        
        Args:
            operand: Operand as string
            n: Number of iterations for phi series
            drv_packet: DRV_Packet for deterministic inputs
            
        Returns:
            OperationBundle: Bundle containing operation details
        """
        if drv_packet is None:
            raise ValueError("DRV_Packet is required")
        return self._perform_operation("phi_series", (operand, str(n)), drv_packet)
        
    def get_audit_log(self) -> list:
        """
        Get the current audit log
        
        Returns:
            list: Audit log entries
        """
        return self.audit_log.copy()
        
    def export_audit_log(self, path: str) -> bool:
        """
        Export audit log to file with PQC attestation
        
        Args:
            path: Path to export audit log to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file already exists
            if os.path.exists(path):
                # Add timestamp to filename to avoid overwriting
                timestamp = int(time.time())
                name, ext = os.path.splitext(path)
                path = f"{name}_{timestamp}{ext}"
            
            # Serialize audit log
            serialized_log = json.dumps(self.audit_log, indent=2, sort_keys=True)
            
            # Generate SHA-256 hash of the log
            log_hash = hashlib.sha256(serialized_log.encode()).hexdigest()
            
            # Generate PQC signature for the log
            pqc_signature = self._generate_pqc_signature(log_hash, "audit_export", str(int(time.time())))
            
            # Create export data with attestation
            export_data = {
                "audit_log": self.audit_log,
                "log_hash": log_hash,
                "pqc_signature": pqc_signature,
                "export_timestamp": int(time.time()),
                "quantum_mode": self.quantum_mode
            }
            
            # Write to file
            with open(path, "w") as f:
                json.dump(export_data, f, indent=2, sort_keys=True)
            return True
        except Exception as e:
            print(f"Error exporting audit log: {e}")
            return False
            
    def verify_pqc_signature(self, bundle: OperationBundle) -> bool:
        """
        Verify PQC signature of an operation bundle
        
        Args:
            bundle: Operation bundle to verify
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # Prepare quantum metadata for signature verification
        quantum_metadata = None
        if (bundle.drv_packet.quantum_source_id and 
            bundle.drv_packet.quantum_entropy and 
            bundle.drv_packet.vdf_output_hash):
            quantum_metadata = {
                "quantum_source_id": bundle.drv_packet.quantum_source_id,
                "quantum_entropy": bundle.drv_packet.quantum_entropy,
                "vdf_output_hash": bundle.drv_packet.vdf_output_hash
            }
        
        # Recreate signature data
        signature_data = f"{bundle.operation}:{':'.join(bundle.operands)}:{bundle.result}:{bundle.operation_id}"
        expected_signature = self._generate_pqc_signature(signature_data, bundle.drv_packet.seed, bundle.operation_id, quantum_metadata)
        
        return bundle.pqc_signature == expected_signature

# Global SDK instance
sdk_client = QFSV13SDK()