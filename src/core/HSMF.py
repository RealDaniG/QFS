"""
HSMF.py - Harmonic Stability & Action Cost Framework (QFS V13.3 Ready)

Fully deterministic, Zero-Simulation Compliant.
PQC logging, DEZ checks, CIR-302 enforcement, Quantum metadata support.
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Import required components
from CertifiedMath import BigNum128, CertifiedMath, PHI
from TokenStateBundle import TokenStateBundle
from CIR302_Handler import CIR302_Handler
    
@dataclass
class ValidationResult:
    """Result from HSMF validation containing all metrics and validation status."""
    is_valid: bool
    dez_ok: bool
    survival_ok: bool
    errors: List[str]
    raw_metrics: Dict[str, BigNum128]
    
    @property
    def metrics_str(self) -> Dict[str, str]:
        """Get string representation of metrics for deterministic serialization."""
        return {k: v.to_decimal_string() for k, v in self.raw_metrics.items()}

# --- HSMF Core ---
class HSMF:

    def __init__(self, cm_instance: CertifiedMath, cir302_handler: Optional[CIR302_Handler] = None):
        """
        Initialize HSMF with a CertifiedMath instance.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            cir302_handler: Optional CIR302 handler for system quarantine
        """
        self.cm = cm_instance
        self.cir302_handler = cir302_handler
        self.ONE = BigNum128.from_int(1)
        self.ZERO = BigNum128.from_int(0)
        self.ONE_PERCENT = CertifiedMath.from_string("0.010000000000000000")

    # --- Core Metrics ---
    def _calculate_I_eff(self, s_chr: BigNum128, beta_penalty: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str] = None) -> BigNum128:
        """Calculate I_eff (effective interest) for HSMF metrics."""
        diff = self.cm.sub(self.ONE, s_chr, log_list, pqc_cid, quantum_meta)
        diff_squared = self.cm.mul(diff, diff, log_list, pqc_cid, quantum_meta)
        s_res = self.cm.mul(beta_penalty, diff_squared, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation("calc_s_res", {"s_chr": s_chr, "beta": beta_penalty}, s_res, log_list, "SRES_PQC" if pqc_cid is None else pqc_cid, quantum_meta)
        return s_res

    def _safe_two_to_the_power(self, exponent: BigNum128, log_list: List[Dict[str, Any]]) -> BigNum128:
        """Wrapper for 2^x calculation using CertifiedMath public API."""
        return self.cm.safe_two_to_the_power(exponent, log_list)

    def _calculate_delta_lambda(self, flx_state: Dict[str, List[BigNum128]], phi_const: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str] = None) -> BigNum128:
        """Calculate delta lambda (flux deviation) for HSMF metrics."""
        magnitudes = flx_state.get("magnitudes", [])
        total_deviation = self.ZERO
        phi = phi_const if isinstance(phi_const, BigNum128) else PHI  # Use precomputed PHI constant

        if len(magnitudes) < 2:
            self.cm._log_operation("calc_s_flx_insufficient_data", {"magnitudes_len": BigNum128.from_int(len(magnitudes))}, total_deviation, log_list)
            return total_deviation

        for i in range(1, len(magnitudes)):
            mag_curr = magnitudes[i]
            mag_prev = magnitudes[i-1]
            if mag_prev.value == 0:
                error_msg = f"Critical S_FLX Zero-Div at index {i-1}"
                if self.cir302_handler:
                    self.cir302_handler.trigger_quarantine(error_msg, {
                        "magnitudes_len": len(magnitudes),
                        "index": i-1
                    })
                else:
                    # Fallback to raising an exception
                    raise RuntimeError(f"CIR-302: {error_msg}")
                return self.ONE
            ratio_actual = self.cm.div(mag_curr, mag_prev, log_list, pqc_cid, quantum_meta)
            # Calculate absolute difference to avoid underflow with unsigned BigNum128
            if self.cm.gte(ratio_actual, phi, log_list, pqc_cid, quantum_meta):
                deviation = self.cm.sub(ratio_actual, phi, log_list, pqc_cid, quantum_meta)
            else:
                deviation = self.cm.sub(phi, ratio_actual, log_list, pqc_cid, quantum_meta)
            abs_deviation = deviation  # deviation is already positive
            total_deviation = self.cm.add(total_deviation, abs_deviation, log_list, pqc_cid, quantum_meta)

        self.cm._log_operation("calc_s_flx_final", {"magnitudes_len": BigNum128.from_int(len(magnitudes)), "phi_const": phi}, total_deviation, log_list, "SFLX_PQC" if pqc_cid is None else pqc_cid, quantum_meta)
        return total_deviation

    def _calculate_delta_h(self, psi_state: Dict[str, BigNum128], drv_packet_sequence: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str] = None) -> BigNum128:
        """Calculate delta h (psi sync deviation) for HSMF metrics."""
        # Use DRV-Packet sequence, NOT timestamp (Section 3.3)
        expected_seq = psi_state.get("current_sequence", self.ZERO)
        # Calculate absolute difference to avoid underflow with unsigned BigNum128
        if self.cm.gte(expected_seq, drv_packet_sequence, log_list, pqc_cid, quantum_meta):
            diff = self.cm.sub(expected_seq, drv_packet_sequence, log_list, pqc_cid, quantum_meta)
        else:
            diff = self.cm.sub(drv_packet_sequence, expected_seq, log_list, pqc_cid, quantum_meta)
        s_psi_sync = diff  # diff is already positive
        self.cm._log_operation("calc_s_psi_sync_final", {"expected_seq": expected_seq, "drv_seq": drv_packet_sequence}, s_psi_sync, log_list, "SPS_PQC" if pqc_cid is None else pqc_cid, quantum_meta)
        return s_psi_sync

    # --- Coherence Checks ---
    def _check_atr_coherence(self, atr_state: Dict[str, BigNum128], f_atr: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str] = None) -> bool:
        """Check ATR coherence for HSMF validation."""
        atr_magnitude = atr_state.get("atr_magnitude", self.ZERO)
        threshold = self.cm.mul(atr_magnitude, self.ONE_PERCENT, log_list, pqc_cid, quantum_meta)
        is_coherent = self.cm.lte(f_atr, threshold, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation("check_atr_coherence", {"f_atr": f_atr, "atr_mag": atr_magnitude}, BigNum128.from_int(1 if is_coherent else 0), log_list, None, quantum_meta)
        return is_coherent

    def _check_directional_encoding(self, f_atr_value: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str] = None) -> bool:
        """Check directional encoding (DEZ structural check) for HSMF validation."""
        is_valid = self.cm.gte(f_atr_value, self.ZERO, log_list, pqc_cid) and self.cm.lte(f_atr_value, self.ONE, log_list, pqc_cid)
        self.cm._log_operation("check_dez_structural", {"f_atr": f_atr_value}, BigNum128.from_int(1 if is_valid else 0), log_list)
        return is_valid

    # --- Composite Metrics ---
    def _calculate_action_cost_qfs(self, s_res: BigNum128, s_flx: BigNum128, s_psi_sync: BigNum128, f_atr: BigNum128, lambda1: BigNum128, lambda2: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str] = None) -> BigNum128:
        """Calculate action cost for HSMF metrics."""
        lambda1_s_flx = self.cm.mul(lambda1, s_flx, log_list, pqc_cid, quantum_meta)
        lambda2_s_psi_sync = self.cm.mul(lambda2, s_psi_sync, log_list, pqc_cid, quantum_meta)
        sum_terms = self.cm.add(s_res, lambda1_s_flx, log_list, pqc_cid, quantum_meta)
        sum_terms = self.cm.add(sum_terms, lambda2_s_psi_sync, log_list, pqc_cid, quantum_meta)
        action_cost = self.cm.add(sum_terms, f_atr, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation("calc_action_cost_qfs", {"s_res": s_res, "s_flx": s_flx, "s_psi_sync": s_psi_sync, "f_atr": f_atr}, action_cost, log_list, "ACQFS_PQC" if pqc_cid is None else pqc_cid, quantum_meta)
        return action_cost

    def _calculate_c_holo(self, s_res: BigNum128, s_flx: BigNum128, s_psi_sync: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str] = None) -> BigNum128:
        """Calculate C_holo (holistic coefficient) for HSMF metrics."""
        # Ensure all operations use CertifiedMath wrappers (Section 3.4)
        # C_holo = 1 / (1 + (s_res + s_flx + s_psi_sync)) (Section 3.4)
        sum_dissonance = self.cm.add(s_res, s_flx, log_list, pqc_cid, quantum_meta)
        sum_dissonance = self.cm.add(sum_dissonance, s_psi_sync, log_list, pqc_cid, quantum_meta)
        one_plus_dissonance = self.cm.add(self.ONE, sum_dissonance, log_list, pqc_cid, quantum_meta)
        c_holo = self.cm.div(self.ONE, one_plus_dissonance, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation("calc_c_holo_final", {"total_dissonance": sum_dissonance}, c_holo, log_list, "CHOLO_PQC" if pqc_cid is None else pqc_cid, quantum_meta)
        return c_holo

    # --- Full Validation ---
    def validate_action_bundle(self, token_bundle: TokenStateBundle, f_atr: BigNum128, 
                              drv_packet_sequence: int,  # Add DRV packet sequence parameter
                              log_list: List[Dict[str, Any]],  # Add log_list parameter
                              pqc_cid: Optional[str] = None, raise_on_failure: bool = False, 
                              strict_atr_coherence: bool = False, quantum_metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate an action bundle using HSMF metrics.
        
        Args:
            token_bundle: TokenStateBundle containing token states
            f_atr: Calculated f(ATR) value
            drv_packet_sequence: DRV packet sequence number for psi sync validation
            log_list: Log list for deterministic audit trail
            pqc_cid: PQC correlation ID
            raise_on_failure: Whether to raise exception on validation failure
            strict_atr_coherence: Whether ATR coherence failures should be treated as hard failures
            quantum_metadata: Quantum metadata for logging
            
        Returns:
            ValidationResult: Validation results containing metrics and status
        """
        errors = []
        is_valid = True
        
        # Check directional encoding (DEZ structural check)
        dez_ok = self._check_directional_encoding(f_atr, log_list, pqc_cid)
        if not dez_ok:
            errors.append("Structural DEZ check failed: f(ATR) must be in [0,1]")
            is_valid = False

        # Check survival imperative: S_CHR > C_CRIT
        survival_ok = self.cm.gte(token_bundle.get_coherence_metric(), token_bundle.c_crit, log_list, pqc_cid, quantum_metadata)
        if not survival_ok:
            errors.append("Survival Imperative failed: S_CHR < C_CRIT")
            is_valid = False

        # Check ATR coherence
        atr_coherent = self._check_atr_coherence(token_bundle.atr_state, f_atr, log_list, quantum_metadata, pqc_cid)
        if not atr_coherent and strict_atr_coherence:
            errors.append("ATR Coherence hard failure due to strict policy")
            is_valid = False

        # Get configuration parameters from token bundle (Section 3.2)
        # Remove hardcoded constants and use token_bundle.parameters
        LAMBDA1 = token_bundle.lambda1
        LAMBDA2 = token_bundle.lambda2
        BETA_PENALTY = token_bundle.parameters.get("beta_penalty", BigNum128.from_int(100000000))
        PHI_CONSTANT = token_bundle.parameters.get("phi", PHI)  # Use precomputed PHI

        # Calculate core metrics
        s_chr = token_bundle.get_coherence_metric()
        s_res = self._calculate_I_eff(s_chr, BETA_PENALTY, log_list, quantum_metadata, pqc_cid)
        s_flx = self._calculate_delta_lambda(token_bundle.flx_state, PHI_CONSTANT, log_list, quantum_metadata, pqc_cid)
        # Use the correct DRV packet sequence number instead of token bundle timestamp (Section 3.3)
        s_psi_sync = self._calculate_delta_h(token_bundle.psi_sync_state, BigNum128.from_int(drv_packet_sequence), log_list, quantum_metadata, pqc_cid)

        # Calculate composite metrics
        action_cost = self._calculate_action_cost_qfs(s_res, s_flx, s_psi_sync, f_atr, LAMBDA1, LAMBDA2, log_list, quantum_metadata, pqc_cid)
        c_holo = self._calculate_c_holo(s_res, s_flx, s_psi_sync, log_list, quantum_metadata, pqc_cid)

        # Log bundle audit reference
        self.cm._log_operation("bundle_audit_ref", {
            "chr": s_chr, 
            "c_crit": token_bundle.c_crit, 
            "f_atr": f_atr
        }, BigNum128.from_int(token_bundle.timestamp), log_list, None, {
            "version": token_bundle.bundle_id if hasattr(token_bundle, 'bundle_id') else "unknown",
            "drv_id": token_bundle.pqc_cid if hasattr(token_bundle, 'pqc_cid') else "unknown"
        })

        # Trigger CIR-302 if configured to do so on failure (Section 3.5)
        if raise_on_failure and not is_valid:
            error_details = f"HSMF Validation Failed. Errors: {'; '.join(errors)}"
            self.cm._log_operation("cir302_trigger", {"error": BigNum128.from_int(1)}, self.ONE, 
                                  log_list, "CIR302_TRIGGER", quantum_metadata)
            if self.cir302_handler:
                self.cir302_handler.trigger_quarantine(error_details, {
                    "token_bundle_id": token_bundle.bundle_id if hasattr(token_bundle, 'bundle_id') else "unknown",
                    "errors": errors
                })
            else:
                raise RuntimeError(f"CIR-302: {error_details}")

        # Log final validation result
        self.cm._log_operation("validate_action_bundle_final_result", {}, 
                              BigNum128.from_int(1 if is_valid else 0), 
                              log_list, pqc_cid, quantum_metadata)

        # Return validation results
        raw_metrics = {
            "action_cost": action_cost, 
            "c_holo": c_holo, 
            "s_res": s_res, 
            "s_flx": s_flx, 
            "s_psi_sync": s_psi_sync, 
            "f_atr": f_atr, 
            "s_chr": s_chr
        }
        
        return ValidationResult(
            is_valid=is_valid, 
            dez_ok=dez_ok, 
            survival_ok=survival_ok, 
            errors=errors, 
            raw_metrics=raw_metrics
        )