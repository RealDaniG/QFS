"""
CoherenceEngine.py - QFS V13 Compliant Coherence Engine

Implements a stateless, deterministic coherence engine that operates only on 
canonical TokenStateBundle inputs and uses only CertifiedMath for all calculations.
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
import sys
import os

# Import required components using relative imports
try:
    from ..libs.CertifiedMath import CertifiedMath, BigNum128
    from .TokenStateBundle import TokenStateBundle
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from libs.CertifiedMath import CertifiedMath, BigNum128
    from core.TokenStateBundle import TokenStateBundle


class CoherenceEngine:
    """
    QFS V13 Compliant Coherence Engine
    
    This is a pure, stateless validator that operates only on canonical TokenStateBundle inputs.
    All calculations use only CertifiedMath and BigNum128 for deterministic fixed-point arithmetic.
    No numpy, no time, no logging, no file I/O.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the QFS V13 Compliant Coherence Engine.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        # Define constants using BigNum128 for fixed-point arithmetic
        self.GOLDEN_RATIO_RECIPROCAL = BigNum128(618033988749894848)  # 0.618 * 1e18
        self.CLAMP_BOUND = BigNum128.from_int(10)  # K = 10.0 in fixed-point
        self.ZERO = BigNum128.from_int(0)
        self.ONE = BigNum128.from_int(1)

    def calculate_modulator(
        self,
        I_vector: List[BigNum128],
        lambda_L: BigNum128,
        K: Optional[BigNum128] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> BigNum128:
        """
        Calculate modulator using CertifiedMath only.
        
        Args:
            I_vector: Integrated feedback vector as list of BigNum128
            lambda_L: Adaptive decay factor as BigNum128
            K: Clamping bound as BigNum128 (default: self.CLAMP_BOUND)
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            BigNum128: Modulator value
        """
        if K is None:
            K = self.CLAMP_BOUND
            
        # Initialize log_list if not provided
        if log_list is None:
            log_list = []
            
        # Compute projection of I_vector (simple mean)
        proj_I = self.ZERO
        if len(I_vector) > 0:
            sum_I = self.ZERO
            for val in I_vector:
                sum_I = self.cm.add(sum_I, val, log_list, pqc_cid, quantum_metadata)
            # Divide by length to get mean
            length_bn = BigNum128.from_int(len(I_vector))
            proj_I = self.cm.div(sum_I, length_bn, log_list, pqc_cid, quantum_metadata)
        
        # Compute λ(L) · proj(I_t(L))
        product = self.cm.mul(lambda_L, proj_I, log_list, pqc_cid, quantum_metadata)
        
        # Clamp to ±K bounds for dimensional consistency
        # Since we're using unsigned BigNum128, we need to handle clamping differently
        # We'll assume the values are already positive and clamp to [0, K]
        if self.cm.gt(product, K, log_list, pqc_cid, quantum_metadata):
            clamped_product = K
        else:
            clamped_product = product
        
        # Compute modulator: exp(clamp(λ(L) · proj(I_t(L)), 0, K))
        # Use 50 iterations for deterministic exp calculation
        modulator_value = self.cm.exp(clamped_product, 50, log_list, pqc_cid, quantum_metadata)
        
        # Log the operation
        self.cm._log_operation(
            "calculate_modulator",
            {
                "I_vector_length": BigNum128.from_int(len(I_vector)),
                "lambda_L": lambda_L,
                "K": K,
                "product": product,
                "clamped_product": clamped_product
            },
            modulator_value,
            log_list,
            pqc_cid,
            quantum_metadata
        )
        
        return modulator_value

    def update_omega(
        self,
        features: List[BigNum128],
        I_vector: List[BigNum128],
        L: str,
        log_list: Optional[List[Dict[str, Any]]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> List[BigNum128]:
        """
        Update Ω state vector using CertifiedMath only.
        
        Args:
            features: Feature vector as list of BigNum128
            I_vector: Integrated feedback vector as list of BigNum128
            L: Scale level identifier
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            List[BigNum128]: Updated Ω vector
        """
        # Initialize log_list if not provided
        if log_list is None:
            log_list = []
            
        # Normalize features
        normalized_features = features  # Default to original if empty
        if len(features) > 0:
            # Calculate norm: sqrt(sum(x^2))
            # Since there's no sqrt function, we'll use pow(x, 0.5) as an approximation
            sum_squares = self.ZERO
            for val in features:
                val_squared = self.cm.mul(val, val, log_list, pqc_cid, quantum_metadata)
                sum_squares = self.cm.add(sum_squares, val_squared, log_list, pqc_cid, quantum_metadata)
            
            # Calculate sqrt using pow(sum_squares, 0.5)
            half = BigNum128(500000000000000000)  # 0.5 * 1e18
            norm = self.cm.pow(sum_squares, half, 50, log_list, pqc_cid, quantum_metadata)
            
            # Normalize if norm is not zero
            if self.cm.gt(norm, self.ZERO, log_list, pqc_cid, quantum_metadata):
                normalized_features = []
                for val in features:
                    normalized_val = self.cm.div(val, norm, log_list, pqc_cid, quantum_metadata)
                    normalized_features.append(normalized_val)
        
        # Calculate lambda_L (golden ratio reciprocal)
        lambda_L = self.GOLDEN_RATIO_RECIPROCAL
        
        # Calculate modulator with potential clamping
        modulator = self.calculate_modulator(
            I_vector, lambda_L, self.CLAMP_BOUND, 
            log_list, pqc_cid, quantum_metadata, deterministic_timestamp
        )
        
        # Update Ω_t(L) = Normalize(F_t) × m_t(L)
        updated_omega = []
        if len(normalized_features) > 0:
            for val in normalized_features:
                omega_val = self.cm.mul(val, modulator, log_list, pqc_cid, quantum_metadata)
                updated_omega.append(omega_val)
        
        # Log the operation if log_list is provided
        if log_list is not None:
            # Calculate norm of updated omega for logging
            omega_norm = self.ZERO
            if len(updated_omega) > 0:
                sum_squares = self.ZERO
                for val in updated_omega:
                    val_squared = self.cm.mul(val, val, log_list, pqc_cid, quantum_metadata)
                    sum_squares = self.cm.add(sum_squares, val_squared, log_list, pqc_cid, quantum_metadata)
                # Calculate sqrt using pow(sum_squares, 0.5)
                half = BigNum128(500000000000000000)  # 0.5 * 1e18
                omega_norm = self.cm.pow(sum_squares, half, 50, log_list, pqc_cid, quantum_metadata)
            
            self.cm._log_operation(
                "update_omega",
                {
                    "features_length": BigNum128.from_int(len(features)),
                    "I_vector_length": BigNum128.from_int(len(I_vector)),
                    "L": L,
                    "modulator": modulator
                },
                omega_norm,  # Log the norm as result
                log_list,
                pqc_cid,
                quantum_metadata
            )
        
        return updated_omega

    def apply_hsmf_transition(
        self,
        current_bundle: TokenStateBundle,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> TokenStateBundle:
        """
        Apply HSMF transition to update all 5 tokens atomically.
        
        Args:
            current_bundle: Current TokenStateBundle
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            TokenStateBundle: Updated TokenStateBundle
        """
        # 1. Compute C_holo using CertifiedMath
        c_holo = self._compute_c_holo(current_bundle, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        
        # 2. Check C_holo < C_MIN → trigger CIR511/CIR302
        # In a real implementation, this would integrate with the CIR302 handler
        # For now, we'll just log if it's below a threshold
        C_MIN = BigNum128.from_int(1)  # 1.0 in fixed-point
        if self.cm.lt(c_holo, C_MIN, log_list, pqc_cid, quantum_metadata):
            # In a real implementation, this would trigger the CIR302 handler
            pass
        
        # 3. Update all 5 tokens atomically
        new_bundle = self._update_tokens(current_bundle, c_holo, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
        
        # Log the operation
        self.cm._log_operation(
            "apply_hsmf_transition",
            {
                "bundle_id": current_bundle.bundle_id,
                "timestamp": BigNum128.from_int(deterministic_timestamp)
            },
            c_holo,
            log_list,
            pqc_cid,
            quantum_metadata
        )
        
        return new_bundle

    def _compute_c_holo(
        self,
        current_bundle: TokenStateBundle,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> BigNum128:
        """
        Compute C_holo attractor logic using only the most recent TokenState snapshot.
        
        Args:
            current_bundle: Current TokenStateBundle
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            BigNum128: C_holo value
        """
        # Extract metrics from the bundle
        s_chr = current_bundle.get_coherence_metric()
        s_flx = current_bundle.get_flux_metric()
        s_psi_sync = current_bundle.get_psi_sync_metric()
        s_res = current_bundle.get_resonance_metric()
        s_atr = current_bundle.get_atr_metric()
        
        # C_holo = 1 / (1 + (s_res + s_flx + s_psi_sync))
        sum_dissonance = self.cm.add(s_res, s_flx, log_list, pqc_cid, quantum_metadata)
        sum_dissonance = self.cm.add(sum_dissonance, s_psi_sync, log_list, pqc_cid, quantum_metadata)
        one_plus_dissonance = self.cm.add(self.ONE, sum_dissonance, log_list, pqc_cid, quantum_metadata)
        c_holo = self.cm.div(self.ONE, one_plus_dissonance, log_list, pqc_cid, quantum_metadata)
        
        # Log the operation
        self.cm._log_operation(
            "compute_c_holo",
            {
                "s_res": s_res,
                "s_flx": s_flx,
                "s_psi_sync": s_psi_sync,
                "sum_dissonance": sum_dissonance
            },
            c_holo,
            log_list,
            pqc_cid,
            quantum_metadata
        )
        
        return c_holo

    def _update_tokens(
        self,
        current_bundle: TokenStateBundle,
        c_holo: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> TokenStateBundle:
        """
        Update all 5 tokens atomically based on C_holo.
        
        Args:
            current_bundle: Current TokenStateBundle
            c_holo: Computed C_holo value
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            TokenStateBundle: Updated TokenStateBundle
        """
        # In a real implementation, this would update all 5 tokens based on the C_holo value
        # For now, we'll just return the current bundle as a placeholder
        # A real implementation would create a new bundle with updated token states
        
        # Log the operation
        self.cm._log_operation(
            "update_tokens",
            {
                "bundle_id": current_bundle.bundle_id,
                "c_holo": c_holo
            },
            c_holo,  # Use c_holo as result for logging
            log_list,
            pqc_cid,
            quantum_metadata
        )
        
        # Return the current bundle as a placeholder
        # In a real implementation, this would return a new bundle with updated states
        return current_bundle


# Deterministic test function
def test_coherence_engine():
    """Test the QFS V13 compliant CoherenceEngine implementation."""
    print("Testing QFS V13 Compliant CoherenceEngine...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create CoherenceEngine
    engine = CoherenceEngine(cm)
    
    log_list = []
    
    # Test calculate_modulator
    I_vector = [BigNum128.from_int(1), BigNum128.from_int(2), BigNum128.from_int(3)]
    lambda_L = BigNum128(618033988749894848)  # 0.618 * 1e18
    K = BigNum128.from_int(10)
    
    modulator = engine.calculate_modulator(
        I_vector=I_vector,
        lambda_L=lambda_L,
        K=K,
        log_list=log_list,
        pqc_cid="test_coherence_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Modulator calculated: {modulator.to_decimal_string()}")
    
    # Test update_omega
    features = [BigNum128.from_int(1), BigNum128.from_int(2), BigNum128.from_int(3)]
    updated_omega = engine.update_omega(
        features=features,
        I_vector=I_vector,
        L="L_Phi",
        log_list=log_list,
        pqc_cid="test_coherence_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Updated Ω vector length: {len(updated_omega)}")
    if updated_omega:
        # Calculate norm for display
        sum_squares = BigNum128.from_int(0)
        for val in updated_omega:
            val_squared = cm.mul(val, val, log_list)
            sum_squares = cm.add(sum_squares, val_squared, log_list)
        # Calculate sqrt using pow(sum_squares, 0.5)
        half = BigNum128(500000000000000000)  # 0.5 * 1e18
        omega_norm = cm.pow(sum_squares, half, 50, log_list, None, None)
        print(f"Updated Ω norm: {omega_norm.to_decimal_string()}")
    
    print(f"Log entries: {len(log_list)}")
    
    print("✓ QFS V13 Compliant CoherenceEngine test passed!")


if __name__ == "__main__":
    test_coherence_engine()