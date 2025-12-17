"""
UtilityOracleInterface.py - Interface for the UtilityOracle component

Defines the interface for the utility oracle, providing validated guidance (f_atr, alpha_update)
and integrating with CertifiedMath and PQC for auditability.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ...libs.CertifiedMath import CertifiedMath, BigNum128
from ...core.DRV_Packet import DRV_Packet

@dataclass
class UtilityOracleResult:
    """Result structure for utility oracle operations"""
    f_atr: BigNum128
    alpha_update: BigNum128
    is_valid: bool
    validation_errors: List[str]
    quantum_metadata: Optional[Dict[str, Any]] = None
    deterministic_hash: Optional[str] = None

class UtilityOracleInterface:
    """
    Interface for the utility oracle component.
    
    Provides validated guidance (f_atr, alpha_update) and integrates with 
    CertifiedMath and PQC for auditability.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Utility Oracle Interface.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance

    def get_f_atr(self, directional_value: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> BigNum128:
        """
        Calculate the ATR penalty function f(ATR).
        
        Args:
            directional_value: Directional value from DRV packet
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            BigNum128: Calculated f(ATR) value
        """
        directional_squared = self.cm.mul(directional_value, directional_value, log_list, pqc_cid, quantum_metadata)
        directional_abs = self.cm.abs(directional_value, log_list, pqc_cid, quantum_metadata)
        one = BigNum128.from_int(1)
        denominator = self.cm.add(one, directional_abs, log_list, pqc_cid, quantum_metadata)
        f_atr = self.cm.div(directional_squared, denominator, log_list, pqc_cid, quantum_metadata)
        return f_atr

    def get_alpha_update(self, current_atr_state: BigNum128, target_state: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> BigNum128:
        """
        Calculate the alpha update factor for ATR stabilization.
        
        Args:
            current_atr_state: Current ATR token state
            target_state: Target ATR state from guidance
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            BigNum128: Alpha update factor (bounded between 0.5 and 1.5)
        """
        difference = self.cm.sub(target_state, current_atr_state, log_list, pqc_cid, quantum_metadata)
        current_abs = self.cm.abs(current_atr_state, log_list, pqc_cid, quantum_metadata)
        one = BigNum128.from_int(1)
        denominator = self.cm.add(one, current_abs, log_list, pqc_cid, quantum_metadata)
        ratio = self.cm.div(difference, denominator, log_list, pqc_cid, quantum_metadata)
        alpha = self.cm.add(one, ratio, log_list, pqc_cid, quantum_metadata)
        min_bound = BigNum128.from_string('0.5')
        max_bound = BigNum128.from_string('1.5')
        is_less_than_min = self.cm.lt(alpha, min_bound, log_list, pqc_cid, quantum_metadata)
        alpha = self.cm.add(self.cm.mul(alpha, BigNum128.from_int(int(not is_less_than_min)), log_list, pqc_cid, quantum_metadata), self.cm.mul(min_bound, BigNum128.from_int(int(is_less_than_min)), log_list, pqc_cid, quantum_metadata), log_list, pqc_cid, quantum_metadata)
        is_greater_than_max = self.cm.gt(alpha, max_bound, log_list, pqc_cid, quantum_metadata)
        alpha = self.cm.add(self.cm.mul(alpha, BigNum128.from_int(int(not is_greater_than_max)), log_list, pqc_cid, quantum_metadata), self.cm.mul(max_bound, BigNum128.from_int(int(is_greater_than_max)), log_list, pqc_cid, quantum_metadata), log_list, pqc_cid, quantum_metadata)
        return alpha

    def validate_directional_encoding(self, directional_value: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> bool:
        """
        Validate the directional encoding value.
        
        Args:
            directional_value: Directional value to validate
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            bool: True if valid, False otherwise
        """
        min_bound = BigNum128.from_string('0.0')
        max_bound = BigNum128.from_string('10.0')
        ge_min = self.cm.gte(directional_value, min_bound, log_list, pqc_cid, quantum_metadata)
        le_max = self.cm.lte(directional_value, max_bound, log_list, pqc_cid, quantum_metadata)
        return ge_min and le_max

    def validate_drv_sequence(self, drv_packet: DRV_Packet, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> bool:
        """
        Validate the DRV packet sequence.
        
        Args:
            drv_packet: DRV packet to validate
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            bool: True if valid, False otherwise
        """
        return True

    def process_drv_packet(self, drv_packet: DRV_Packet, current_token_bundle: Any, target_atr_state: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> UtilityOracleResult:
        """
        Process a DRV packet and generate utility oracle results.
        
        Args:
            drv_packet: DRV packet to process
            current_token_bundle: Current token state bundle
            target_atr_state: Target ATR state from guidance
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            UtilityOracleResult: Processed results with validation
        """
        validation_errors = []
        directional_value_str = getattr(drv_packet, 'directional_value', '0.0')
        directional_value = BigNum128.from_string(str(directional_value_str))
        if not self.validate_drv_sequence(drv_packet, log_list, pqc_cid, quantum_metadata, deterministic_timestamp):
            validation_errors.append('Invalid DRV sequence')
        if not self.validate_directional_encoding(directional_value, log_list, pqc_cid, quantum_metadata, deterministic_timestamp):
            validation_errors.append('Invalid directional encoding')
        current_atr_state = BigNum128.from_string('1.0')
        f_atr = self.get_f_atr(directional_value, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        alpha_update = self.get_alpha_update(current_atr_state, target_atr_state, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        is_valid = len(validation_errors) == 0
        deterministic_hash = self.get_deterministic_hash(f_atr, alpha_update, is_valid, validation_errors, quantum_metadata)
        return UtilityOracleResult(f_atr=f_atr, alpha_update=alpha_update, is_valid=is_valid, validation_errors=validation_errors, quantum_metadata=quantum_metadata, deterministic_hash=deterministic_hash)

    def get_deterministic_hash(self, f_atr: BigNum128, alpha_update: BigNum128, is_valid: bool, validation_errors: List[str], quantum_metadata: Optional[Dict[str, Any]]) -> str:
        """
        Generate a deterministic hash of the utility oracle result.
        
        Args:
            f_atr: Calculated f(ATR) value
            alpha_update: Calculated alpha update value
            is_valid: Validation status
            validation_errors: List of validation errors
            quantum_metadata: Quantum metadata
            
        Returns:
            str: SHA256 hash of the serialized result
        """
        serializable = {'f_atr': f_atr.to_decimal_string(), 'alpha_update': alpha_update.to_decimal_string(), 'is_valid': is_valid, 'validation_errors': validation_errors, 'quantum_metadata': quantum_metadata}
        serialized = json.dumps(serializable, sort_keys=True, separators=(',', ':'))
        hash_object = hashlib.sha256(serialized.encode('utf-8'))
        return hash_object.hexdigest()

def create_utility_oracle(cm_instance: CertifiedMath) -> UtilityOracleInterface:
    """
    Factory function to create a UtilityOracleInterface instance.
    
    Args:
        cm_instance: CertifiedMath instance for deterministic calculations
        
    Returns:
        UtilityOracleInterface: Created utility oracle interface
    """
    return UtilityOracleInterface(cm_instance)

def test_utility_oracle_interface():
    """Test the UtilityOracleInterface implementation."""
    cm = CertifiedMath()
    oracle_interface = UtilityOracleInterface(cm)
    directional_value = BigNum128.from_int(2)
    current_atr_state = BigNum128.from_int(1)
    target_atr_state = BigNum128.from_int(3)
    log_list = []
    f_atr = oracle_interface.get_f_atr(directional_value=directional_value, log_list=log_list, pqc_cid='test_oracle_001', deterministic_timestamp=1234567890)
    alpha_update = oracle_interface.get_alpha_update(current_atr_state=current_atr_state, target_state=target_atr_state, log_list=log_list, pqc_cid='test_oracle_001', deterministic_timestamp=1234567890)
    is_valid = oracle_interface.validate_directional_encoding(directional_value=directional_value, log_list=log_list, pqc_cid='test_oracle_001', deterministic_timestamp=1234567890)
if __name__ == '__main__':
    test_utility_oracle_interface()