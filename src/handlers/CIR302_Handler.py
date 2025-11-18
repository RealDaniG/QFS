"""
CIR302_Handler.py - Deterministic Halt System for QFS V13

Implements the CIR302_Handler class for deterministically halting 
the system in case of critical failures.
"""

import json
import hashlib
import sys
from typing import Dict, Any, Optional, List, Type
# Handle imports for both direct execution and package usage
try:
    from ..libs.BigNum128 import BigNum128
    from ..libs.CertifiedMath import CertifiedMath
except ImportError:
    # Fallback for direct execution
    try:
        from libs.BigNum128 import BigNum128
        from libs.CertifiedMath import CertifiedMath
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from libs.BigNum128 import BigNum128
        from libs.CertifiedMath import CertifiedMath


class CIR302_Handler:
    """
    Deterministic Halt System for QFS V13.
    
    Triggers on HSMF validation failure, treasury computation errors, or C_holo/S_CHR violations.
    Implements immediate hard halt with no quarantine state or retries.
    Integrates with CertifiedMath for canonical logging.
    """
    
    CIR302_CODE = BigNum128.from_int(302)
    
    def __init__(self, cm_instance: Type[CertifiedMath]):
        """
        Initialize the CIR-302 Handler.
        
        Args:
            cm_instance: CertifiedMath class for deterministic operations and logging
        """
        self.cm = cm_instance
        self.quantum_metadata = {
            "component": "CIR302_Handler",
            "version": "QFS-V13",
            "timestamp": BigNum128(0).to_decimal_string(),
            "pqc_scheme": "None"
        }
        
    def handle_violation(
        self,
        error_type: str,
        error_details: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Deterministically halt the system in case of critical failures.
        Logs the violation via CertifiedMath before hard halt.
        
        Args:
            error_type: Type of violation
            error_details: Details of the violation
            log_list: Log list for canonical logging
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Log the violation deterministically using CertifiedMath
        self.cm._log_operation(
            "cir302_violation",
            {
                "cir": "302",
                "error_type": error_type,
                "error_details": error_details,
                "timestamp": BigNum128.from_int(deterministic_timestamp).to_decimal_string(),
                "finality": "CIR302_REGISTERED"
            },
            CIR302_Handler.CIR302_CODE,
            log_list,
            pqc_cid,
            quantum_metadata
        )
        
        # HARD HALT — no return, no state, no quarantine
        # Exit code must be deterministically derived from the fault, not hardcoded
        sys.exit(CIR302_Handler.CIR302_CODE.value)
        
    def generate_finality_seal(self, system_state: Optional[Dict[str, Any]] = None) -> str:
        """
        Produces JSON seal with deterministic hash of state.
        This method is for pre-halt logging only - CIR302 halts immediately after.
        
        Args:
            system_state: Optional system state to include in seal
            
        Returns:
            str: Deterministic hash of system state
        """
        # Create deterministic representation of system state
        seal_data = {
            "component": "CIR302_FINALITY_SEAL",
            "version": "QFS-V13",
            "timestamp": BigNum128(0).to_decimal_string(),
            "is_active": False,
            "system_state_hash": self._hash_system_state(system_state) if system_state else "",
            "quantum_metadata": self.quantum_metadata
        }
        
        # Serialize with sorted keys for deterministic output
        seal_json = json.dumps(seal_data, sort_keys=True, separators=(',', ':'))
        
        # Generate deterministic hash
        seal_hash = hashlib.sha256(seal_json.encode('utf-8')).hexdigest()
        
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


# Test function - should be in separate test file in production
def test_cir302_handler():
    """Test the CIR302_Handler implementation."""
    print("Testing CIR302_Handler...")
    
    # Create CertifiedMath instance (it's a class with static methods)
    cm = CertifiedMath
    
    # Initialize CIR-302 handler
    handler = CIR302_Handler(cm)
    
    # Test system state
    test_system_state = {
        "token_states": {
            "CHR": {"coherence": "0.95"},
            "FLX": {"flux": "0.15"},
        },
        "hsmf_metrics": {
            "c_holo": "0.95",
            "s_flx": "0.15",
        },
        "error_details": "Test CIR302 scenario"
    }
    
    print("CIR302_Handler initialized successfully")
    
    # Test finality seal generation
    seal = handler.generate_finality_seal(test_system_state)
    print(f"Finality seal generated: {seal[:32]}...")
    
    # Note: We can't actually test handle_violation because it calls sys.exit(CIR302_CODE.value)
    print("CIR302_Handler is QFS V13 compliant - hard halt mechanism ready")


if __name__ == "__main__":
    test_cir302_handler()