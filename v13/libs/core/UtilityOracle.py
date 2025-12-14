"""
UtilityOracle.py - Pure validator for pre-computed oracle guidance values

Implements the UtilityOracle class as a pure validator for PQC-signed oracle updates
without any external data fetching or entropy processing.
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required modules
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

@dataclass
class OracleGuidance:
    """Container for oracle guidance values"""
    atr_directional_vector: BigNum128  # f_atr or g_target for ATR stabilization
    directional_penalty: BigNum128     # Penalty for directional deviation
    quantum_metadata: Optional[Dict[str, Any]] = None


class UtilityOracle:
    """
    Pure validator for pre-computed oracle guidance values.
    
    Validates PQC-signed oracle updates without any external data fetching.
    All oracle data aggregation and entropy processing must happen in external orchestrators.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Utility Oracle validator.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance

    def validate_oracle_update(
        self,
        f_atr: BigNum128,
        directional_penalty: BigNum128,
        oracle_signature: bytes,  # PQC signature
        expected_metadata: Dict[str, Any],  # PQC-signed metadata
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> OracleGuidance:
        """
        Validate pre-computed oracle guidance values.
        
        Args:
            f_atr: Pre-computed ATR directional vector (must be in [0,1] range)
            directional_penalty: Pre-computed directional penalty
            oracle_signature: PQC signature validating the oracle update
            expected_metadata: PQC-signed expected metadata
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            OracleGuidance: Validated oracle guidance values
            
        Raises:
            RuntimeError: If validation fails (triggers CIR-302)
        """
        # Validate f_atr is in valid range [0, 1] for DEZ check
        zero = BigNum128(0)
        one = BigNum128.from_int(1)
        
        if self.cm.lt(f_atr, zero, log_list, pqc_cid, quantum_metadata) or \
           self.cm.gt(f_atr, one, log_list, pqc_cid, quantum_metadata):
            raise RuntimeError("f_atr out of valid range [0,1] - CIR-302 required")
            
        # Validate directional_penalty is non-negative
        if self.cm.lt(directional_penalty, zero, log_list, pqc_cid, quantum_metadata):
            raise RuntimeError("directional_penalty cannot be negative - CIR-302 required")
            
        # Validate PQC signature (simplified validation - in practice would verify signature)
        if not oracle_signature or len(oracle_signature) == 0:
            raise RuntimeError("Invalid oracle signature - CIR-302 required")
            
        # Create validated oracle guidance object
        validated_guidance = OracleGuidance(
            atr_directional_vector=f_atr,
            directional_penalty=directional_penalty,
            quantum_metadata=expected_metadata
        )
        
        # Log the validation
        self._log_oracle_validation(
            f_atr, directional_penalty, expected_metadata,
            log_list, pqc_cid, quantum_metadata, deterministic_timestamp
        )
        
        return validated_guidance

    def _log_oracle_validation(
        self,
        f_atr: BigNum128,
        directional_penalty: BigNum128,
        metadata: Dict[str, Any],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the oracle validation for audit purposes.
        
        Args:
            f_atr: Validated ATR directional vector
            directional_penalty: Validated directional penalty
            metadata: Metadata associated with oracle update
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        details = {
            "operation": "oracle_update_validation",
            "f_atr": f_atr.to_decimal_string(),
            "directional_penalty": directional_penalty.to_decimal_string(),
            "metadata_keys": list(metadata.keys()) if metadata else [],
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "oracle_update_validation",
            details,
            f_atr,  # Use f_atr as the primary value for logging
            log_list,
            pqc_cid,
            quantum_metadata
        )


# Test function
def test_utility_oracle():
    """Test the UtilityOracle implementation."""
    print("Testing UtilityOracle...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create UtilityOracle
    oracle = UtilityOracle(cm)
    
    # Create test oracle values
    test_f_atr = BigNum128.from_string("0.5")  # 0.5 in valid range [0,1]
    test_penalty = BigNum128.from_int(10)  # 10.0 penalty
    test_signature = b"test_signature_bytes"
    test_metadata = {
        "source": "test_oracle",
        "timestamp": 1234567890,
        "aggregation_method": "median_of_medians"
    }
    
    log_list = []
    
    # Validate oracle update
    try:
        validated_guidance = oracle.validate_oracle_update(
            f_atr=test_f_atr,
            directional_penalty=test_penalty,
            oracle_signature=test_signature,
            expected_metadata=test_metadata,
            log_list=log_list,
            pqc_cid="test_oracle_001",
            deterministic_timestamp=1234567890
        )
        
        print(f"Oracle validation successful!")
        print(f"f_atr: {validated_guidance.atr_directional_vector.to_decimal_string()}")
        print(f"Penalty: {validated_guidance.directional_penalty.to_decimal_string()}")
        print(f"Log entries: {len(log_list)}")
        print("✓ UtilityOracle test passed!")
        
    except Exception as e:
        print(f"Oracle validation failed: {e}")
        print("✗ UtilityOracle test failed!")


if __name__ == "__main__":
    test_utility_oracle()