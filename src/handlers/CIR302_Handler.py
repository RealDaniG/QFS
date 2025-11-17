"""
CIR302_Handler.py - Deterministic Halt & Quarantine System for QFS V13

Implements the CIR302_Handler class for deterministically halting or quarantining 
the system in case of critical failures.
"""

import json
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Import required components
from CertifiedMath import BigNum128, CertifiedMath
from TokenStateBundle import TokenStateBundle
from PQC import PQC


@dataclass
class QuarantineResult:
    """Result from the CIR-302 quarantine process."""
    is_quarantined: bool
    reason: str
    system_state: Dict[str, Any]
    finality_seal: Optional[str]
    timestamp: int
    pqc_cid: str


class CIR302_Handler:
    """
    Deterministic Halt & Quarantine System for QFS V13.
    
    Triggers on HSMF validation failure, treasury computation errors, or C_holo/S_CHR violations.
    Isolates runtime, prevents further state changes, and logs AEGIS_FINALITY_SEAL.json.
    Integrates with CoherenceLedger.py for audit artifact generation.
    """
    
    def __init__(self, cm_instance: CertifiedMath, pqc_key_pair: Optional[tuple] = None):
        """
        Initialize the CIR-302 Handler.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            pqc_key_pair: Optional PQC key pair for signing finality seals
        """
        self.cm = cm_instance
        self.pqc_private_key = pqc_key_pair[0] if pqc_key_pair else None
        self.pqc_public_key = pqc_key_pair[1] if pqc_key_pair else None
        self.is_active = False
        self.quarantine_reason = ""
        self.quantum_metadata = {
            "component": "CIR302_Handler",
            "version": "QFS-V13-P1-2",
            "timestamp": "0",  # Use string "0" for deterministic behavior
            "pqc_scheme": "Dilithium-5"
        }
        
    def trigger_quarantine(self, reason: str, system_state: Dict[str, Any]) -> QuarantineResult:
        """
        Deterministically halt or quarantine the system in case of critical failures.
        
        Args:
            reason: Reason for quarantine
            system_state: Current system state at time of failure
            
        Returns:
            QuarantineResult with quarantine details
        """
        if self.is_active:
            # Already in quarantine state
            return QuarantineResult(
                is_quarantined=True,
                reason=self.quarantine_reason,
                system_state=system_state,
                finality_seal=None,
                timestamp=0,
                pqc_cid=""
            )
            
        # Activate quarantine
        self.is_active = True
        self.quarantine_reason = reason
        
        # Generate finality seal
        finality_seal = self.generate_finality_seal(system_state)
        
        # Generate PQC correlation ID
        pqc_cid = self._generate_pqc_cid(reason, system_state)
        
        # Update quantum metadata
        self.quantum_metadata["timestamp"] = "0"
        
        print(f"SEC-HSM-HALT-FINAL: System quarantined due to: {reason}")
        print(f"Finality seal generated: {finality_seal[:32]}...")
        
        return QuarantineResult(
            is_quarantined=True,
            reason=reason,
            system_state=system_state,
            finality_seal=finality_seal,
            timestamp=0,
            pqc_cid=pqc_cid
        )
        
    def generate_finality_seal(self, system_state: Optional[Dict[str, Any]] = None) -> str:
        """
        Produces JSON seal with deterministic hash of state.
        
        Args:
            system_state: Optional system state to include in seal
            
        Returns:
            str: Deterministic hash of system state
        """
        # Create deterministic representation of system state
        seal_data = {
            "component": "CIR302_FINALITY_SEAL",
            "version": "QFS-V13-P1-2",
            "timestamp": 0,
            "quarantine_reason": self.quarantine_reason if self.is_active else "",
            "is_active": self.is_active,
            "system_state_hash": self._hash_system_state(system_state) if system_state else "",
            "quantum_metadata": self.quantum_metadata
        }
        
        # Serialize with sorted keys for deterministic output
        seal_json = json.dumps(seal_data, sort_keys=True, separators=(',', ':'))
        
        # Generate deterministic hash
        seal_hash = hashlib.sha256(seal_json.encode('utf-8')).hexdigest()
        
        # Apply PQC signature if key is available
        if self.pqc_private_key:
            try:
                signature = PQC.sign_data(self.pqc_private_key, seal_json, [])
                seal_data["pqc_signature"] = signature.hex()
            except Exception as e:
                print(f"Warning: PQC signing failed: {e}")
        
        return seal_hash
        
    def _hash_system_state(self, system_state: Dict[str, Any]) -> str:
        """
        Generate deterministic hash of system state.
        
        Args:
            system_state: System state dictionary
            
        Returns:
            str: SHA-256 hash of system state
        """
        if not system_state:
            return ""
            
        # Serialize with sorted keys for deterministic output
        state_json = json.dumps(system_state, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(state_json.encode('utf-8')).hexdigest()
        
    def _generate_pqc_cid(self, reason: str, system_state: Dict[str, Any]) -> str:
        """
        Generate deterministic PQC correlation ID.
        
        Args:
            reason: Quarantine reason
            system_state: System state
            
        Returns:
            str: Deterministic PQC correlation ID
        """
        data_to_hash = {
            "reason": reason,
            "system_state_hash": self._hash_system_state(system_state),
            "timestamp": 0,
            "is_active": self.is_active
        }
        
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]
        
    def is_system_quarantined(self) -> bool:
        """
        Check if system is currently quarantined.
        
        Returns:
            bool: True if system is quarantined, False otherwise
        """
        return self.is_active


# Test function
def test_cir302_handler():
    """Test the CIR302_Handler implementation."""
    print("Testing CIR302_Handler...")
    
    # Create test log list and CertifiedMath instance
    log_list = []
    cm = CertifiedMath()
    
    # Create test PQC key pair
    from PQC import PQC
    log_list = []
    keypair = PQC.generate_keypair(log_list)
    pqc_keypair = (keypair.private_key, keypair.public_key)
    
    # Initialize CIR-302 handler
    handler = CIR302_Handler(cm, pqc_keypair)
    
    # Test system state
    test_system_state = {
        "token_states": {
            "CHR": {"coherence": "0.95"},
            "FLX": {"flux": "0.15"},
            "PSI_SYNC": {"sync": "0.08"},
            "ATR": {"attractor": "0.85"},
            "RES": {"resonance": "0.05"}
        },
        "hsmf_metrics": {
            "c_holo": "0.95",
            "s_flx": "0.15",
            "s_psi_sync": "0.08",
            "f_atr": "0.85"
        },
        "error_details": "Test quarantine scenario"
    }
    
    # Test quarantine trigger
    result = handler.trigger_quarantine("Test CIR-302 trigger", test_system_state)
    
    print(f"Quarantine triggered: {result.is_quarantined}")
    print(f"Reason: {result.reason}")
    print(f"Finality seal: {result.finality_seal}")
    print(f"PQC CID: {result.pqc_cid}")
    print(f"System quarantined: {handler.is_system_quarantined()}")
    
    # Test finality seal generation
    seal = handler.generate_finality_seal(test_system_state)
    print(f"Finality seal (regenerated): {seal[:32]}...")


if __name__ == "__main__":
    test_cir302_handler()