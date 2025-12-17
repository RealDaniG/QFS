from libs.deterministic_helpers import det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
from libs.fatal_errors import ZeroSimAbort, EconomicInvariantBreach, GovernanceGuardFailure
from typing import Dict, Any, Optional
from enum import Enum
try:
    from v13.core.TokenStateBundle import TokenStateBundle
except ImportError:
    try:
        from v13.core.TokenStateBundle import TokenStateBundle
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from v13.core.TokenStateBundle import TokenStateBundle

class EconomicViolation(Enum):
    CHR_CONSERVATION_BREACH = 'CHR_CONSERVATION_BREACH'
    NEGATIVE_FLOW_ATTEMPT = 'NEGATIVE_FLOW_ATTEMPT'
    FLX_FLOW_IMBALANCE = 'FLX_FLOW_IMBALANCE'
    PSY_MONOTONICITY_VIOLATION = 'PSY_MONOTONICITY_VIOLATION'
    ATTR_ATTRACTOR_VIOLATION = 'ATTR_ATTRACTOR_VIOLATION'
    RES_ENVELOPE_BREACH = 'RES_ENVELOPE_BREACH'
    HARMONIC_DIVERGENCE = 'HARMONIC_DIVERGENCE'

class EconomicSecurityError(Exception):
    """Security violation in harmonic economic computations."""

    def __init__(self, message: str, violation_type: EconomicViolation, evidence: Dict=None, cir_code: str=None):
        super().__init__(message)
        self.violation_type = violation_type
        self.evidence = evidence or {}
        self.cir_code = cir_code

class NullEventLogger:
    """Default no-op event logger."""

    def log(self, category: str, event_type: str, data: Dict, timestamp: int):
        pass

class HarmonicEconomics:
    """
    PRODUCTION-HARDENED 5-token economics engine.

    Enforces:
    - CHR conservation (EA-5 protection)
    - FLX flow balance with ψ-gradient proportionality (EA-6 protection)
    - ΨSync monotonicity with coherence
    - ATR attractor law
    - RES bounded by resonance envelope (EA-4 protection)
    """

    def __init__(self, psi_field_engine: Any, certified_math: Any, event_logger: Any=None):
        """
        Initialize with ψ-field physics and certified mathematics.

        Args:
            psi_field_engine: DiscretePsiField instance from Step 1
            certified_math: QFS V13 CertifiedMath instance
            event_logger: Structured event logger for evidence generation
        """
        self.psi_field = psi_field_engine
        self.math = certified_math
        self.event_logger = event_logger or NullEventLogger()
        self.economic_state_history = []
        self.violation_counters = {violation: 0 for violation in EconomicViolation}
        self.FLUX_PROPORTIONALITY_CONSTANT = 1000
        self.MAX_RESONANCE_ENVELOPE = 10 ** 9
        self.MIN_ATTRACTOR_INCREMENT = 1
        self.DISSONANCE_PENALTY_BASE = 1000
        self.SCALE_FACTOR = 1000000

    def compute_harmonic_state(self, current_state: TokenStateBundle) -> TokenStateBundle:
        """
        Compute full 5-token harmonic state with economic law enforcement.

        Args:
            current_state: Input TokenStateBundle with current 5-token state

        Returns:
            New TokenStateBundle with validated economic transformations

        Raises:
            EconomicSecurityError: For economic rule violations (CIR-302/412/511)
            ValueError: For invalid inputs or state inconsistencies
            SecurityError: For ψ-field integrity violations (from PsiFieldEngine)
        """
        new_state = self._deep_copy_state(current_state)
        try:
            self._validate_economic_invariants(current_state)
            psi_metrics = self.psi_field.validate_psi_field_integrity(current_state, delta_curl_threshold=current_state.parameters['δ_curl'].value)
            new_state = self._apply_token_transformations(current_state, new_state, psi_metrics)
            self._validate_economic_invariants(new_state)
            self._update_economic_history(current_state, new_state)
            self._log_harmonic_event('STATE_TRANSITION_SUCCESS', {'old_state_hash': self._compute_state_hash(current_state), 'new_state_hash': self._compute_state_hash(new_state), 'psi_sync_change': self._compute_psi_sync_change(current_state, new_state)})
            return new_state
        except EconomicSecurityError as e:
            raise
        except Exception as e:
            self._log_harmonic_event('STATE_TRANSITION_FAILURE', {'error': str(e), 'current_state_hash': self._compute_state_hash(current_state)})
            raise EconomicSecurityError(f'Unexpected error during harmonic state computation: {str(e)}', EconomicViolation.HARMONIC_DIVERGENCE)

    def _apply_token_transformations(self, old_state: TokenStateBundle, new_state: TokenStateBundle, psi_metrics: Dict) -> TokenStateBundle:
        """
        Apply economic transformations while preserving all conservation laws.
        """
        old_shards = old_state.chr_state.get('shards', {})
        new_shards = new_state.chr_state.get('shards', {})
        for shard_id in new_shards.keys():
            shard = new_shards[shard_id]
            old_shard = old_shards[shard_id]
            if shard['CHR'] != old_shard['CHR']:
                self._handle_economic_violation(EconomicViolation.CHR_CONSERVATION_BREACH, f"CHR conservation violation in {shard_id}: {old_shard['CHR']} -> {shard['CHR']}", shard_id)
            shard['FLX'] = self._compute_flux_balance(shard_id, old_state, new_state, psi_metrics)
            shard['ΨSync'] = self._compute_psisync_update(shard_id, old_shard, shard, psi_metrics)
            shard['ATR'] = self._compute_attractor_update(shard_id, old_shard, shard, psi_metrics)
            shard['RES'] = self._compute_resonance_update(shard_id, old_shard, shard, psi_metrics)
            shard['DISSONANCE'] = self._compute_dissonance_penalty(shard_id, old_state, new_state)
        return new_state

    def _compute_flux_balance(self, shard_id: str, old_state: TokenStateBundle, new_state: TokenStateBundle, psi_metrics: Dict) -> int:
        """
        Enforce FLX flow balance: inflow = outflow with ψ-gradient proportionality.
        Implements Kirchhoff's current law for token flows.
        """
        old_shards = old_state.chr_state.get('shards', {})
        new_shards = new_state.chr_state.get('shards', {})
        shard = new_shards[shard_id]
        old_flx = old_shards[shard_id]['FLX']
        net_flow = 0
        neighbors = self.psi_field.graph.get(shard_id, set())
        for neighbor in sorted(neighbors):
            if shard_id < neighbor:
                gradient = psi_metrics['psi_gradients'].get((shard_id, neighbor), 0)
                flow_magnitude = self.math.mul(self.math.abs(gradient), self.FLUX_PROPORTIONALITY_CONSTANT) // self.SCALE_FACTOR
                if gradient > 0:
                    net_flow = self.math.add(net_flow, flow_magnitude)
                else:
                    net_flow = self.math.sub(net_flow, flow_magnitude)
        new_flx = self.math.add(old_flx, net_flow)
        if new_flx < 0:
            self._handle_economic_violation(EconomicViolation.NEGATIVE_FLOW_ATTEMPT, f'Negative FLX in {shard_id}: {old_flx} -> {new_flx}', shard_id)
            return 0
        return new_flx

    def _compute_psisync_update(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any], psi_metrics: Dict) -> int:
        """
        Compute ΨSync update enforcing monotonicity with coherence.
        ΨSync must increase or stay constant when coherence increases.
        """
        old_psi_density = self.psi_field.psi_density(shard_id, TokenStateBundle(chr_state={'shards': {shard_id: {'CHR': old_shard['CHR'], 'ATR': old_shard['ATR'], 'DISSONANCE': old_shard.get('DISSONANCE', 0)}}}, flx_state={}, psi_sync_state={}, atr_state={}, res_state={}, signature='', timestamp=0, bundle_id='temp', pqc_cid='temp', quantum_metadata={}, lambda1=self.math.ONE, lambda2=self.math.ONE, c_crit=self.math.ONE, parameters={}))
        new_psi_density = self.psi_field.psi_density(shard_id, TokenStateBundle(chr_state={'shards': {shard_id: {'CHR': new_shard['CHR'], 'ATR': new_shard['ATR'], 'DISSONANCE': new_shard.get('DISSONANCE', 0)}}}, flx_state={}, psi_sync_state={}, atr_state={}, res_state={}, signature='', timestamp=0, bundle_id='temp', pqc_cid='temp', quantum_metadata={}, lambda1=self.math.ONE, lambda2=self.math.ONE, c_crit=self.math.ONE, parameters={}))
        coherence_change = self.math.sub(new_psi_density, old_psi_density)
        old_psisync = old_shard['ΨSync']
        if coherence_change > 0:
            new_psisync = self.math.add(old_psisync, self.math.div_floor(coherence_change, 100))
            return max(old_psisync, new_psisync)
        else:
            max_decrease = self.math.div_floor(old_psisync, 10)
            return self.math.sub(old_psisync, min(max_decrease, abs(coherence_change // 1000)))

    def _compute_attractor_update(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any], psi_metrics: Dict) -> int:
        """
        Enforce monotonic attractor law: ATR increases with stability.
        Prevents sudden collapse of field stability anchors.
        """
        old_atr = old_shard['ATR']
        stability_metric = self._compute_stability_metric(shard_id, old_shard, new_shard)
        if stability_metric < -5000:
            max_decrease = self.math.div_floor(old_atr, 20)
            return self.math.sub(old_atr, max_decrease)
        else:
            increment = self.math.max(self.MIN_ATTRACTOR_INCREMENT, self.math.div_floor(stability_metric, 1000))
            return self.math.add(old_atr, increment)

    def _compute_resonance_update(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any], psi_metrics: Dict) -> int:
        """
        Compute RES update bounded by system resonance envelope.
        Prevents resonance overdrive attacks (EA-4).
        """
        old_res = old_shard['RES']
        resonance_generation = 0
        neighbors = self.psi_field.graph.get(shard_id, set())
        for neighbor in sorted(neighbors):
            alignment = self._compute_shard_alignment(shard_id, neighbor, TokenStateBundle(chr_state={'shards': {shard_id: {'CHR': old_shard['CHR'], 'ATR': old_shard['ATR']}}}, flx_state={}, psi_sync_state={}, atr_state={}, res_state={}, signature='', timestamp=0, bundle_id='temp', pqc_cid='temp', quantum_metadata={}, lambda1=self.math.ONE, lambda2=self.math.ONE, c_crit=self.math.ONE, parameters={}))
            resonance_generation = self.math.add(resonance_generation, alignment)
        new_res = self.math.add(old_res, resonance_generation)
        envelope = self._compute_resonance_envelope(shard_id, new_shard)
        if new_res > envelope:
            self._handle_economic_violation(EconomicViolation.RES_ENVELOPE_BREACH, f'RES envelope breach in {shard_id}: {new_res} > {envelope}', shard_id)
            return envelope
        return new_res

    def _compute_dissonance_penalty(self, shard_id: str, old_state: TokenStateBundle, new_state: TokenStateBundle) -> int:
        """
        Compute dissonance penalty for economic misalignment.
        Used in ψ-density calculations to reduce coherence during imbalances.
        """
        new_shards = new_state.chr_state.get('shards', {})
        shard = new_shards[shard_id]
        flow_imbalance = self._compute_flow_imbalance(shard_id, new_state)
        chr_anomaly = self._compute_chr_distribution_anomaly(shard_id, new_state)
        total_dissonance = self.math.add(flow_imbalance, chr_anomaly)
        return self.math.min(total_dissonance, 10 ** 6)

    def _validate_economic_invariants(self, state: TokenStateBundle):
        """
        Validate all economic invariants with precise violation detection.
        """
        violations = []
        shards = state.chr_state.get('shards', {})
        total_chr = sum((shard['CHR'] for shard in shards.values()))
        expected_chr = getattr(state.parameters.get('MAX_CHR_SUPPLY'), 'value', 10000000000)
        if total_chr != expected_chr:
            violations.append((EconomicViolation.CHR_CONSERVATION_BREACH, f'Global CHR conservation: {total_chr} != {expected_chr}'))
        for shard_id in shards:
            flow_imbalance = self._compute_flow_imbalance(shard_id, state)
            delta_max = getattr(state.parameters.get('δ_max'), 'value', 5)
            if self.math.abs(flow_imbalance) > delta_max * 1000:
                violations.append((EconomicViolation.FLX_FLOW_IMBALANCE, f'FLX flow imbalance in {shard_id}: {flow_imbalance}'))
        if len(self.economic_state_history) >= 2:
            current_sync = sum((shard['ΨSync'] for shard in shards.values()))
            previous_sync = sum((shard['ΨSync'] for shard in self.economic_state_history[-1].chr_state.get('shards', {}).values()))
            epsilon_sync = getattr(state.parameters.get('ε_sync'), 'value', 2)
            if current_sync < previous_sync - epsilon_sync * 100:
                violations.append((EconomicViolation.PSY_MONOTONICITY_VIOLATION, f'ΨSync monotonicity violation: {current_sync} < {previous_sync}'))
        for shard_id, shard in shards.items():
            if shard['ATR'] < 0:
                violations.append((EconomicViolation.ATTR_ATTRACTOR_VIOLATION, f"Negative ATR in {shard_id}: {shard['ATR']}"))
        for violation_type, message in violations:
            self._handle_economic_violation(violation_type, message)

    def _compute_flow_imbalance(self, shard_id: str, state: TokenStateBundle) -> int:
        """Compute FLX inflow - outflow for a shard."""
        inflow, outflow = (0, 0)
        flow_matrix = state.flx_state.get('FLX_flow_matrix', {})
        for (src, dst), flow in flow_matrix.items():
            if dst == shard_id:
                inflow = self.math.add(inflow, flow)
            if src == shard_id:
                outflow = self.math.add(outflow, flow)
        return self.math.sub(inflow, outflow)

    def _compute_chr_distribution_anomaly(self, shard_id: str, state: TokenStateBundle) -> int:
        """Compute CHR distribution anomaly metric."""
        shards = state.chr_state.get('shards', {})
        shard_chr = shards[shard_id]['CHR']
        avg_chr = sum((s['CHR'] for s in shards.values())) // len(shards)
        deviation = self.math.abs(self.math.sub(shard_chr, avg_chr))
        return self.math.div_floor(deviation, 1000)

    def _compute_stability_metric(self, shard_id: str, old_shard: Dict[str, Any], new_shard: Dict[str, Any]) -> int:
        """Compute stability metric for ATR updates."""
        chr_stability = self.math.sub(new_shard['CHR'], old_shard['CHR'])
        flx_stability = self.math.sub(new_shard['FLX'], old_shard['FLX']) // 1000
        return self.math.add(chr_stability, flx_stability)

    def _compute_shard_alignment(self, shard_a: str, shard_b: str, old_state: TokenStateBundle) -> int:
        """Compute alignment metric between two shards for RES generation."""
        shards = old_state.chr_state.get('shards', {})
        if shard_a not in shards or shard_b not in shards:
            return 0
        shard_a_data = shards[shard_a]
        shard_b_data = shards[shard_b]
        chr_alignment = self.math.min(shard_a_data['CHR'], shard_b_data['CHR'])
        atr_alignment = self.math.min(shard_a_data['ATR'], shard_b_data['ATR'])
        return self.math.div_floor(self.math.mul(chr_alignment, atr_alignment), self.SCALE_FACTOR)

    def _compute_resonance_envelope(self, shard_id: str, new_shard: Dict[str, Any]) -> int:
        """Compute maximum RES capacity for a shard."""
        base_envelope = self.math.mul(new_shard['CHR'], new_shard['ATR']) // self.SCALE_FACTOR
        return self.math.min(base_envelope, self.MAX_RESONANCE_ENVELOPE)

    def _handle_economic_violation(self, violation_type: EconomicViolation, message: str, shard_id: str=None):
        """Handle economic violations with deterministic exception raising."""
        self.violation_counters[violation_type] += 1
        evidence = {'violation_type': violation_type.value, 'message': message, 'shard_id': shard_id, 'counter': self.violation_counters[violation_type], 'cir_code': self._get_cir_code_for_violation(violation_type)}
        self._log_harmonic_event('ECONOMIC_VIOLATION', evidence)
        cir_code = self._get_cir_code_for_violation(violation_type)
        raise EconomicSecurityError(message=f'{cir_code}: {message}', violation_type=violation_type, evidence=evidence, cir_code=cir_code)

    def _get_cir_code_for_violation(self, violation_type: EconomicViolation) -> str:
        """Deterministic mapping from economic violations to CIR codes."""
        mapping = {EconomicViolation.CHR_CONSERVATION_BREACH: 'CIR-302', EconomicViolation.NEGATIVE_FLOW_ATTEMPT: 'CIR-302', EconomicViolation.FLX_FLOW_IMBALANCE: 'CIR-302', EconomicViolation.PSY_MONOTONICITY_VIOLATION: 'CIR-412', EconomicViolation.ATTR_ATTRACTOR_VIOLATION: 'CIR-412', EconomicViolation.RES_ENVELOPE_BREACH: 'CIR-511'}
        return mapping.get(violation_type, 'CIR-302')

    def _update_economic_history(self, old_state: TokenStateBundle, new_state: TokenStateBundle):
        """Maintain economic state history for monotonicity proofs."""
        if len(self.economic_state_history) >= 10:
            self.economic_state_history.pop(0)
        self.economic_state_history.append(self._deep_copy_state(new_state))

    def _deep_copy_state(self, state: TokenStateBundle) -> TokenStateBundle:
        """Create safe copy of TokenStateBundle for transformation."""
        try:
            return state.copy()
        except AttributeError:
            import copy
            return copy.deepcopy(state)

    def _compute_state_hash(self, state: TokenStateBundle) -> str:
        """Compute deterministic hash of economic state for evidence.

        NOTE: SHA3-256 is permitted in evidence layer per QFSV13 §8.3
        """
        import hashlib
        import json
        shards = state.chr_state.get('shards', {})
        state_dict = {'shards': {k: {'CHR': v['CHR'], 'FLX': v['FLX'], 'ATR': v['ATR'], 'RES': v['RES'], 'ΨSync': v['ΨSync'], 'DISSONANCE': v.get('DISSONANCE', 0)} for k, v in shards.items()}, 'system_constants': {'MAX_CHR_SUPPLY': state.parameters['MAX_CHR_SUPPLY'].value, 'δ_max': state.parameters['δ_max'].value, 'ε_sync': state.parameters['ε_sync'].value}}
        canonical = json.dumps(state_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha3_256(canonical.encode()).hexdigest()

    def _compute_psi_sync_change(self, old_state: TokenStateBundle, new_state: TokenStateBundle) -> int:
        """Compute change in global ΨSync for monitoring."""
        old_shards = old_state.chr_state.get('shards', {})
        new_shards = new_state.chr_state.get('shards', {})
        old_sync = sum((shard['ΨSync'] for shard in old_shards.values()))
        new_sync = sum((shard['ΨSync'] for shard in new_shards.values()))
        return self.math.sub(new_sync, old_sync)

    def _log_harmonic_event(self, event_type: str, data: Dict):
        """Log harmonic economic events for evidence and audit trails."""
        timestamp = getattr(data, 'timestamp', 0)
        self.event_logger.log(category='HARMONIC_ECONOMICS', event_type=event_type, data=data, timestamp=timestamp)

    def get_economic_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive economic health report for evidence."""
        return {'violation_summary': {v.value: count for v, count in self.violation_counters.items()}, 'state_history_size': len(self.economic_state_history), 'economic_constants': {'flux_proportionality': self.FLUX_PROPORTIONALITY_CONSTANT, 'max_resonance_envelope': self.MAX_RESONANCE_ENVELOPE, 'min_attractor_increment': self.MIN_ATTRACTOR_INCREMENT}}
if __name__ == '__main__':
    pass
__all__ = ['HarmonicEconomics', 'EconomicViolation', 'EconomicSecurityError']