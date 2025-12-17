"""
gating_service.py - QFS V13 Compliant Gating Service

Implements a stateless validator for GAS calculation, memory locking, and safe mode triggers
using only CertifiedMath and BigNum128 for deterministic fixed-point arithmetic.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
try:
    from ..libs.CertifiedMath import CertifiedMath, BigNum128
    from .TokenStateBundle import TokenStateBundle
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from v13.libs.CertifiedMath import CertifiedMath, BigNum128
    from v13.core.TokenStateBundle import TokenStateBundle

@dataclass
class GatingMetrics:
    """Metrics for gating service using BigNum128 for deterministic values"""
    gas: BigNum128
    cs: BigNum128
    rsi: BigNum128
    safe_mode_active: bool
    timestamp: BigNum128

class GatingService:
    """
    QFS V13 Compliant Gating Service
    
    This is a pure, stateless validator that operates only on canonical inputs.
    All calculations use only CertifiedMath and BigNum128 for deterministic fixed-point arithmetic.
    No numpy, no time, no logging, no file I/O.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the QFS V13 Compliant Gating Service.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        self.ZERO = BigNum128.from_int(0)
        self.ONE = BigNum128.from_int(1)
        self.GAS_NORMALIZATION_FACTOR = BigNum128(100000000000000000000000000000000000000)
        self.CS_THRESHOLD = BigNum128(800000000000000000)
        self.GAS_THRESHOLD = BigNum128(990000000000000000)
        self.RSI_SAFE_THRESHOLD = BigNum128(650000000000000000)
        self.GAS_SAFE_THRESHOLD = BigNum128(900000000000000000)

    def calculate_GAS(self, R_Omega_tensor: List[List[BigNum128]], geometric_eigenvalues: Dict[str, int], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> BigNum128:
        """
        Calculate Geometric Alignment Score (GAS) using CertifiedMath only.
        
        Args:
            R_Omega_tensor: Resonant Curvature Tensor as list of lists of BigNum128
            geometric_eigenvalues: Dictionary with quantum numbers Q(n, ℓ, m, s) as integers
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            BigNum128: Geometric Alignment Score (0.0 to 1.0)
        """
        tensor_norm = self.ZERO
        for i in range(len(R_Omega_tensor)):
            row = R_Omega_tensor[i]
            for j in range(len(row)):
                element = row[j]
                element_squared = self.cm.mul(element, element, log_list, pqc_cid, quantum_metadata)
                tensor_norm = self.cm.add(tensor_norm, element_squared, log_list, pqc_cid, quantum_metadata)
        half = BigNum128(500000000000000000)
        tensor_norm = self.cm.pow(tensor_norm, half, 50, log_list, pqc_cid, quantum_metadata)
        n = geometric_eigenvalues.get('n', 1)
        l = geometric_eigenvalues.get('l', 0)
        m = geometric_eigenvalues.get('m', 0)
        s = geometric_eigenvalues.get('s', 500000000000000000)
        n_bn = BigNum128.from_int(n)
        l_bn = BigNum128.from_int(l)
        m_bn = BigNum128.from_int(abs(m))
        s_bn = BigNum128(s)
        n_squared = self.cm.mul(n_bn, n_bn, log_list, pqc_cid, quantum_metadata)
        l_squared = self.cm.mul(l_bn, l_bn, log_list, pqc_cid, quantum_metadata)
        m_squared = self.cm.mul(m_bn, m_bn, log_list, pqc_cid, quantum_metadata)
        s_squared = self.cm.mul(s_bn, s_bn, log_list, pqc_cid, quantum_metadata)
        sum_squares = self.cm.add(n_squared, l_squared, log_list, pqc_cid, quantum_metadata)
        sum_squares = self.cm.add(sum_squares, m_squared, log_list, pqc_cid, quantum_metadata)
        sum_squares = self.cm.add(sum_squares, s_squared, log_list, pqc_cid, quantum_metadata)
        quantum_alignment = self.cm.pow(sum_squares, half, 50, log_list, pqc_cid, quantum_metadata)
        ten = BigNum128.from_int(10)
        quantum_alignment = self.cm.div(quantum_alignment, ten, log_list, pqc_cid, quantum_metadata)
        if self.cm.gt(tensor_norm, self.ZERO, log_list, pqc_cid, quantum_metadata):
            product = self.cm.mul(tensor_norm, quantum_alignment, log_list, pqc_cid, quantum_metadata)
            gas = self.cm.div(product, self.GAS_NORMALIZATION_FACTOR, log_list, pqc_cid, quantum_metadata)
            if self.cm.gt(gas, self.ONE, log_list, pqc_cid, quantum_metadata):
                gas = self.ONE
        else:
            gas = self.ZERO
        self.cm._log_operation('calculate_GAS', {'tensor_norm': tensor_norm, 'quantum_alignment': quantum_alignment, 'n': n_bn, 'l': l_bn, 'm': m_bn, 's': s_bn}, gas, log_list, pqc_cid, quantum_metadata)
        return gas

    def apply_memory_lock(self, coherence_stability: BigNum128, gas: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> bool:
        """
        Apply memory write lock based on dual thresholds using CertifiedMath only.
        
        Args:
            coherence_stability: Current coherence stability (CS) as BigNum128
            gas: Geometric Alignment Score as BigNum128
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            bool: True if memory locked, False otherwise
        """
        cs_ok = self.cm.gte(coherence_stability, self.CS_THRESHOLD, log_list, pqc_cid, quantum_metadata)
        gas_ok = self.cm.gte(gas, self.GAS_THRESHOLD, log_list, pqc_cid, quantum_metadata)
        should_lock = not (cs_ok and gas_ok)
        self.cm._log_operation('apply_memory_lock', {'coherence_stability': coherence_stability, 'gas': gas, 'cs_threshold': self.CS_THRESHOLD, 'gas_threshold': self.GAS_THRESHOLD, 'cs_ok': BigNum128.from_int(1 if cs_ok else 0), 'gas_ok': BigNum128.from_int(1 if gas_ok else 0)}, BigNum128.from_int(1 if should_lock else 0), log_list, pqc_cid, quantum_metadata)
        return should_lock

    def check_safe_mode_trigger(self, rsi: BigNum128, gas: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> bool:
        """
        Check if Safe Mode should be triggered using CertifiedMath only.
        
        Args:
            rsi: Recursive Stability Index as BigNum128
            gas: Geometric Alignment Score as BigNum128
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            bool: True if Safe Mode activated, False otherwise
        """
        rsi_low = self.cm.lt(rsi, self.RSI_SAFE_THRESHOLD, log_list, pqc_cid, quantum_metadata)
        gas_low = self.cm.lt(gas, self.GAS_SAFE_THRESHOLD, log_list, pqc_cid, quantum_metadata)
        should_trigger = rsi_low or gas_low
        self.cm._log_operation('check_safe_mode_trigger', {'rsi': rsi, 'gas': gas, 'rsi_threshold': self.RSI_SAFE_THRESHOLD, 'gas_threshold': self.GAS_SAFE_THRESHOLD, 'rsi_low': BigNum128.from_int(1 if rsi_low else 0), 'gas_low': BigNum128.from_int(1 if gas_low else 0)}, BigNum128.from_int(1 if should_trigger else 0), log_list, pqc_cid, quantum_metadata)
        return should_trigger

    def get_current_metrics(self, R_Omega_tensor: List[List[BigNum128]], geometric_eigenvalues: Dict[str, int], coherence_stability: BigNum128, rsi: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> GatingMetrics:
        """
        Get current gating metrics using CertifiedMath only.
        
        Args:
            R_Omega_tensor: Resonant Curvature Tensor as list of lists of BigNum128
            geometric_eigenvalues: Dictionary with quantum numbers as integers
            coherence_stability: Current coherence stability as BigNum128
            rsi: Recursive Stability Index as BigNum128
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            GatingMetrics: Current metrics
        """
        gas = self.calculate_GAS(R_Omega_tensor, geometric_eigenvalues, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        memory_locked = self.apply_memory_lock(coherence_stability, gas, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        safe_mode_active = self.check_safe_mode_trigger(rsi, gas, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        metrics = GatingMetrics(gas=gas, cs=coherence_stability, rsi=rsi, safe_mode_active=safe_mode_active, timestamp=BigNum128.from_int(deterministic_timestamp))
        self.cm._log_operation('get_current_metrics', {'gas': gas, 'cs': coherence_stability, 'rsi': rsi, 'safe_mode_active': BigNum128.from_int(1 if safe_mode_active else 0), 'memory_locked': BigNum128.from_int(1 if memory_locked else 0)}, BigNum128.from_int(deterministic_timestamp), log_list, pqc_cid, quantum_metadata)
        return metrics

    def validate_precomputed_metrics(self, gas: BigNum128, cs: BigNum128, rsi: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0) -> GatingMetrics:
        """
        Validate precomputed metrics (stateless validator pattern).
        
        Args:
            gas: Precomputed Geometric Alignment Score as BigNum128
            cs: Precomputed Coherence Stability as BigNum128
            rsi: Precomputed Recursive Stability Index as BigNum128
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            GatingMetrics: Validated metrics
        """
        memory_locked = self.apply_memory_lock(cs, gas, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        safe_mode_active = self.check_safe_mode_trigger(rsi, gas, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        metrics = GatingMetrics(gas=gas, cs=cs, rsi=rsi, safe_mode_active=safe_mode_active, timestamp=BigNum128.from_int(deterministic_timestamp))
        self.cm._log_operation('validate_precomputed_metrics', {'gas': gas, 'cs': cs, 'rsi': rsi, 'safe_mode_active': BigNum128.from_int(1 if safe_mode_active else 0), 'memory_locked': BigNum128.from_int(1 if memory_locked else 0)}, BigNum128.from_int(deterministic_timestamp), log_list, pqc_cid, quantum_metadata)
        return metrics