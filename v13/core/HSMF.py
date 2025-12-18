"""
HSMF.py - Harmonic Stability & Action Cost Framework (QFS V13.3 Ready)

Fully deterministic, Zero-Simulation Compliant.
PQC logging, DEZ checks, CIR-302 enforcement, Quantum metadata support.
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
try:
    from ..libs.CertifiedMath import BigNum128, CertifiedMath
    from .TokenStateBundle import TokenStateBundle
    from ..handlers.CIR302_Handler import CIR302_Handler
    from ..libs.integration.StateTransitionEngine import StateTransitionEngine
    from ..libs.governance.RewardAllocator import AllocatedReward
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
        from v13.core.TokenStateBundle import TokenStateBundle
        from handlers.CIR302_Handler import CIR302_Handler
        from v13.libs.integration.StateTransitionEngine import StateTransitionEngine
        from v13.libs.governance.RewardAllocator import AllocatedReward
    except ImportError:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
        from v13.core.TokenStateBundle import TokenStateBundle
        from handlers.CIR302_Handler import CIR302_Handler
        from v13.libs.integration.StateTransitionEngine import StateTransitionEngine

@dataclass
class ValidationResult:
    """Result from HSMF validation containing all metrics and validation status."""
    is_valid: bool
    dez_ok: bool
    survival_ok: bool
    errors: List[str]
    raw_metrics: Dict[str, BigNum128]

    @property
    def metrics(self) -> Dict[str, str]:
        """Return decimal-string representations of metrics"""
        return dict(sorted(((k, v.to_decimal_string()) for k, v in self.raw_metrics.items())))

class HSMF:

    def __init__(self, cm_instance: CertifiedMath, cir302_handler: Optional[CIR302_Handler]=None, state_transition_engine: Optional[StateTransitionEngine]=None):
        """
        Initialize HSMF with a CertifiedMath instance.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            cir302_handler: Optional CIR302 handler for system quarantine
            state_transition_engine: Optional StateTransitionEngine for atomic updates
        """
        self.cm = cm_instance
        self.cir302_handler = cir302_handler
        self.state_transition_engine = state_transition_engine
        self.ONE = BigNum128.from_int(1)
        self.ZERO = BigNum128.from_int(0)
        self.ONE_PERCENT = BigNum128(10000000000000000)
        self.PHI = BigNum128(1618033988749894848)

    def _calculate_I_eff(self, s_chr: BigNum128, beta_penalty: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str]=None) -> BigNum128:
        """Calculate I_eff (effective interest) for HSMF metrics."""
        diff = self.cm.sub(self.ONE, s_chr, log_list, pqc_cid, quantum_meta)
        diff_squared = self.cm.mul(diff, diff, log_list, pqc_cid, quantum_meta)
        s_res = self.cm.mul(beta_penalty, diff_squared, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation('calc_s_res', {'s_chr': s_chr, 'beta': beta_penalty}, s_res, log_list, 'SRES_PQC' if pqc_cid is None else pqc_cid, quantum_meta)
        return s_res

    def _safe_two_to_the_power(self, exponent: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None) -> BigNum128:
        """Wrapper for 2^x calculation using CertifiedMath public API."""
        return self.cm.two_to_the_power(exponent, 50, log_list, pqc_cid, quantum_metadata)

    def _calculate_delta_lambda(self, flx_state: Dict[str, List[BigNum128]], phi_const: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str]=None) -> BigNum128:
        """Calculate delta lambda (flux deviation) for HSMF metrics."""
        magnitudes = flx_state.get('magnitudes', [])
        total_deviation = self.ZERO
        phi = phi_const if isinstance(phi_const, BigNum128) else self.PHI
        if len(magnitudes) < 2:
            self.cm._log_operation('calc_s_flx_insufficient_data', {'magnitudes_len': BigNum128.from_int(len(magnitudes))}, total_deviation, log_list)
            return total_deviation
        for i in range(1, len(magnitudes)):
            mag_curr = magnitudes[i]
            mag_prev = magnitudes[i - 1]
            if mag_prev.value == 0:
                error_msg = f'Critical S_FLX Zero-Div at index {i - 1}'
                if self.cir302_handler:
                    self.cir302_handler.handle_violation('s_flx_zero_division', error_msg, log_list, pqc_cid, quantum_meta, 0)
                else:
                    raise RuntimeError(f'CIR-302: {error_msg}')
                return self.ONE
            ratio_actual = self.cm.div(mag_curr, mag_prev, log_list, pqc_cid, quantum_meta)
            if self.cm.gte(ratio_actual, phi, log_list, pqc_cid, quantum_meta):
                deviation = self.cm.sub(ratio_actual, phi, log_list, pqc_cid, quantum_meta)
            else:
                deviation = self.cm.sub(phi, ratio_actual, log_list, pqc_cid, quantum_meta)
            abs_deviation = deviation
            total_deviation = self.cm.add(total_deviation, abs_deviation, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation('calc_s_flx_final', {'magnitudes_len': BigNum128.from_int(len(magnitudes)), 'phi_const': phi}, total_deviation, log_list, 'SFLX_PQC' if pqc_cid is None else pqc_cid, quantum_meta)
        return total_deviation

    def _calculate_delta_h(self, psi_state: Dict[str, BigNum128], drv_packet_sequence: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str]=None) -> BigNum128:
        """Calculate delta h (psi sync deviation) for HSMF metrics."""
        expected_seq = psi_state.get('current_sequence', self.ZERO)
        if self.cm.gte(expected_seq, drv_packet_sequence, log_list, pqc_cid, quantum_meta):
            diff = self.cm.sub(expected_seq, drv_packet_sequence, log_list, pqc_cid, quantum_meta)
        else:
            diff = self.cm.sub(drv_packet_sequence, expected_seq, log_list, pqc_cid, quantum_meta)
        s_psi_sync = diff
        self.cm._log_operation('calc_s_psi_sync_final', {'expected_seq': expected_seq, 'drv_seq': drv_packet_sequence}, s_psi_sync, log_list, 'SPS_PQC' if pqc_cid is None else pqc_cid, quantum_meta)
        return s_psi_sync

    def _check_atr_coherence(self, atr_state: Dict[str, BigNum128], f_atr: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str]=None) -> bool:
        """Check ATR coherence for HSMF validation."""
        atr_magnitude = atr_state.get('atr_magnitude', self.ZERO)
        threshold = self.cm.mul(atr_magnitude, self.ONE_PERCENT, log_list, pqc_cid, quantum_meta)
        is_coherent = self.cm.lte(f_atr, threshold, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation('check_atr_coherence', {'f_atr': f_atr, 'atr_mag': atr_magnitude}, BigNum128.from_int(1 if is_coherent else 0), log_list, None, quantum_meta)
        return is_coherent

    def _check_directional_encoding(self, f_atr_value: BigNum128, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None) -> bool:
        """Check directional encoding (DEZ structural check) for HSMF validation."""
        is_valid = self.cm.gte(f_atr_value, self.ZERO, log_list, pqc_cid) and self.cm.lte(f_atr_value, self.ONE, log_list, pqc_cid)
        self.cm._log_operation('check_dez_structural', {'f_atr': f_atr_value}, BigNum128.from_int(1 if is_valid else 0), log_list)
        return is_valid

    def _calculate_action_cost_qfs(self, s_res: BigNum128, s_flx: BigNum128, s_psi_sync: BigNum128, f_atr: BigNum128, lambda1: BigNum128, lambda2: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str]=None) -> BigNum128:
        """Calculate action cost for HSMF metrics."""
        lambda1_s_flx = self.cm.mul(lambda1, s_flx, log_list, pqc_cid, quantum_meta)
        lambda2_s_psi_sync = self.cm.mul(lambda2, s_psi_sync, log_list, pqc_cid, quantum_meta)
        sum_terms = self.cm.add(s_res, lambda1_s_flx, log_list, pqc_cid, quantum_meta)
        sum_terms = self.cm.add(sum_terms, lambda2_s_psi_sync, log_list, pqc_cid, quantum_meta)
        action_cost = self.cm.add(sum_terms, f_atr, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation('calc_action_cost_qfs', {'s_res': s_res, 's_flx': s_flx, 's_psi_sync': s_psi_sync, 'f_atr': f_atr}, action_cost, log_list, 'ACQFS_PQC' if pqc_cid is None else pqc_cid, quantum_meta)
        return action_cost

    def _calculate_c_holo(self, s_res: BigNum128, s_flx: BigNum128, s_psi_sync: BigNum128, log_list: List[Dict[str, Any]], quantum_meta: Optional[Dict[str, Any]], pqc_cid: Optional[str]=None) -> BigNum128:
        """Calculate C_holo (holistic coefficient) for HSMF metrics."""
        sum_dissonance = self.cm.add(s_res, s_flx, log_list, pqc_cid, quantum_meta)
        sum_dissonance = self.cm.add(sum_dissonance, s_psi_sync, log_list, pqc_cid, quantum_meta)
        one_plus_dissonance = self.cm.add(self.ONE, sum_dissonance, log_list, pqc_cid, quantum_meta)
        c_holo = self.cm.div(self.ONE, one_plus_dissonance, log_list, pqc_cid, quantum_meta)
        self.cm._log_operation('calc_c_holo_final', {'total_dissonance': sum_dissonance}, c_holo, log_list, 'CHOLO_PQC' if pqc_cid is None else pqc_cid, quantum_meta)
        return c_holo

    def apply_hsmf_transition(self, current_bundle: TokenStateBundle, f_atr: BigNum128, drv_packet_sequence: int, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0, recipient_addresses: Optional[List[str]]=None) -> TokenStateBundle:
        """
        Apply HSMF transition with atomic 5-token update enforcement.
        
        Args:
            current_bundle: Current TokenStateBundle
            f_atr: Calculated f(ATR) value
            drv_packet_sequence: DRV packet sequence number
            log_list: Log list for deterministic audit trail
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata for logging
            deterministic_timestamp: Deterministic timestamp
            recipient_addresses: List of recipient addresses for reward allocation
            
        Returns:
            TokenStateBundle: New token state bundle after atomic transition
            
        Raises:
            RuntimeError: If state transition engine is not configured
        """
        result = self.validate_action_bundle(current_bundle, f_atr, drv_packet_sequence, log_list, pqc_cid, raise_on_failure=False, quantum_metadata=quantum_metadata)
        if not result.is_valid:
            error_details = f"HSMF Transition Failed. Errors: {'; '.join(result.errors)}"
            if self.cir302_handler:
                self.cir302_handler.handle_violation('hsmf_transition_failure', error_details, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
            else:
                raise RuntimeError(f'CIR-302: {error_details}')
        rewards = self._compute_hsmf_rewards(result.raw_metrics, log_list, pqc_cid, quantum_metadata)
        allocated_rewards = {}
        if self.state_transition_engine and recipient_addresses:
            from ..libs.governance.RewardAllocator import RewardAllocator
            reward_allocator = RewardAllocator(self.cm)
            from ..libs.governance.TreasuryEngine import RewardBundle
            reward_bundle = RewardBundle(chr_reward=rewards.get('chr_reward', self.ZERO), flx_reward=rewards.get('flx_reward', self.ZERO), res_reward=rewards.get('res_reward', self.ZERO), psi_sync_reward=rewards.get('psi_sync_reward', self.ZERO), atr_reward=rewards.get('atr_reward', self.ZERO), total_reward=rewards.get('total_reward', self.ZERO))
            allocated_rewards = reward_allocator.allocate_rewards(reward_bundle=reward_bundle, recipient_addresses=recipient_addresses, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp)
        if self.state_transition_engine:
            transition_result = self.state_transition_engine.apply_state_transition(current_bundle, allocated_rewards, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
            if not transition_result.success:
                error_details = f'Atomic State Transition Failed: {transition_result.error_message}'
                if self.cir302_handler:
                    self.cir302_handler.handle_violation('state_transition_failure', error_details, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
                else:
                    raise RuntimeError(f'CIR-302: {error_details}')
            if transition_result.new_token_bundle is None:
                error_details = f'Atomic State Transition Failed: No token bundle returned'
                if self.cir302_handler:
                    self.cir302_handler.handle_violation('state_transition_failure', error_details, log_list, pqc_cid, quantum_metadata, deterministic_timestamp)
                else:
                    raise RuntimeError(f'CIR-302: {error_details}')
            return transition_result.new_token_bundle
        else:
            raise RuntimeError('StateTransitionEngine not configured for atomic 5-token updates')

    def _compute_hsmf_rewards(self, metrics: Dict[str, BigNum128], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None) -> Dict[str, BigNum128]:
        """
        Compute reward allocations for all 5 tokens based on HSMF metrics.
        
        Args:
            metrics: HSMF metrics from validation
            log_list: Log list for deterministic audit trail
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata for logging
            
        Returns:
            Dict[str, BigNum128]: Reward allocations for each token type
        """
        action_cost = metrics.get('action_cost', self.ZERO)
        c_holo = metrics.get('c_holo', self.ZERO)
        s_res = metrics.get('s_res', self.ZERO)
        s_flx = metrics.get('s_flx', self.ZERO)
        s_psi_sync = metrics.get('s_psi_sync', self.ZERO)
        f_atr = metrics.get('f_atr', self.ZERO)
        s_chr = metrics.get('s_chr', self.ZERO)
        chr_reward = self.cm.mul(s_chr, c_holo, log_list, pqc_cid, quantum_metadata)
        flx_reward = self.cm.mul(s_flx, action_cost, log_list, pqc_cid, quantum_metadata)
        res_reward = self.cm.mul(s_res, c_holo, log_list, pqc_cid, quantum_metadata)
        psi_sync_reward = self.cm.mul(s_psi_sync, f_atr, log_list, pqc_cid, quantum_metadata)
        atr_reward = self.cm.mul(f_atr, c_holo, log_list, pqc_cid, quantum_metadata)
        total_reward = self.cm.add(self.cm.add(chr_reward, flx_reward, log_list, pqc_cid, quantum_metadata), self.cm.add(self.cm.add(res_reward, psi_sync_reward, log_list, pqc_cid, quantum_metadata), atr_reward, log_list, pqc_cid, quantum_metadata), log_list, pqc_cid, quantum_metadata)
        return {'chr_reward': chr_reward, 'flx_reward': flx_reward, 'res_reward': res_reward, 'psi_sync_reward': psi_sync_reward, 'atr_reward': atr_reward, 'total_reward': total_reward}

    def validate_action_bundle(self, token_bundle: TokenStateBundle, f_atr: BigNum128, drv_packet_sequence: int, log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, raise_on_failure: bool=False, strict_atr_coherence: bool=False, quantum_metadata: Optional[Dict[str, Any]]=None) -> ValidationResult:
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
        '\n        Validate an action bundle using HSMF metrics.\n        \n        Args:\n            token_bundle: TokenStateBundle containing token states\n            f_atr: Calculated f(ATR) value\n            drv_packet_sequence: DRV packet sequence number for psi sync validation\n            log_list: Log list for deterministic audit trail\n            pqc_cid: PQC correlation ID\n            raise_on_failure: Whether to raise exception on validation failure\n            strict_atr_coherence: Whether ATR coherence failures should be treated as hard failures\n            quantum_metadata: Quantum metadata for logging\n            \n        Returns:\n            ValidationResult: Validation results containing metrics and status\n        '
        errors = []
        is_valid = True
        dez_ok = self._check_directional_encoding(f_atr, log_list, pqc_cid)
        if not dez_ok:
            errors.append('Structural DEZ check failed: f(ATR) must be in [0,1]')
            is_valid = False
        survival_ok = self.cm.gte(token_bundle.get_coherence_metric(), token_bundle.c_crit, log_list, pqc_cid, quantum_metadata)
        if not survival_ok:
            errors.append('Survival Imperative failed: S_CHR < C_CRIT')
            is_valid = False
        atr_coherent = self._check_atr_coherence(token_bundle.atr_state, f_atr, log_list, quantum_metadata, pqc_cid)
        if not atr_coherent and strict_atr_coherence:
            errors.append('ATR Coherence hard failure due to strict policy')
            is_valid = False
        LAMBDA1 = token_bundle.lambda1
        LAMBDA2 = token_bundle.lambda2
        BETA_PENALTY = token_bundle.parameters.get('beta_penalty', BigNum128.from_int(100000000))
        PHI_CONSTANT = token_bundle.parameters.get('phi', self.PHI)
        s_chr = token_bundle.get_coherence_metric()
        s_res = self._calculate_I_eff(s_chr, BETA_PENALTY, log_list, quantum_metadata, pqc_cid)
        s_flx = self._calculate_delta_lambda(token_bundle.flx_state, PHI_CONSTANT, log_list, quantum_metadata, pqc_cid)
        s_psi_sync = self._calculate_delta_h(token_bundle.psi_sync_state, BigNum128.from_int(drv_packet_sequence), log_list, quantum_metadata, pqc_cid)
        action_cost = self._calculate_action_cost_qfs(s_res, s_flx, s_psi_sync, f_atr, LAMBDA1, LAMBDA2, log_list, quantum_metadata, pqc_cid)
        c_holo = self._calculate_c_holo(s_res, s_flx, s_psi_sync, log_list, quantum_metadata, pqc_cid)
        self.cm._log_operation('bundle_audit_ref', {'chr': s_chr, 'c_crit': token_bundle.c_crit, 'f_atr': f_atr}, BigNum128.from_int(token_bundle.timestamp), log_list, None, {'version': token_bundle.bundle_id if hasattr(token_bundle, 'bundle_id') else 'unknown', 'drv_id': token_bundle.pqc_cid if hasattr(token_bundle, 'pqc_cid') else 'unknown'})
        if raise_on_failure and (not is_valid):
            error_details = f"HSMF Validation Failed. Errors: {'; '.join(errors)}"
            self.cm._log_operation('cir302_trigger', {'error': BigNum128.from_int(1)}, self.ONE, log_list, 'CIR302_TRIGGER', quantum_metadata)
            if self.cir302_handler:
                self.cir302_handler.handle_violation('hsmf_validation_failure', error_details, log_list, pqc_cid, quantum_metadata, drv_packet_sequence)
            else:
                raise RuntimeError(f'CIR-302: {error_details}')
        self.cm._log_operation('validate_action_bundle_final_result', {}, BigNum128.from_int(1 if is_valid else 0), log_list, pqc_cid, quantum_metadata)
        raw_metrics = {'action_cost': action_cost, 'c_holo': c_holo, 's_res': s_res, 's_flx': s_flx, 's_psi_sync': s_psi_sync, 'f_atr': f_atr, 's_chr': s_chr}
        return ValidationResult(is_valid=is_valid, dez_ok=dez_ok, survival_ok=survival_ok, errors=errors, raw_metrics=raw_metrics)
