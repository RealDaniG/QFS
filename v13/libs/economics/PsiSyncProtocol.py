from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
from libs.fatal_errors import ZeroSimAbort, EconomicInvariantBreach, GovernanceGuardFailure
from typing import Any, Dict, List, Optional
from v13.libs.DeterministicTime import DeterministicTime
from v13.libs.CertifiedMath import BigNum128

class SecurityError(Exception):
    """Custom exception for security violations."""

    def __init__(self, message, violation_type, evidence, cir_code):
        super().__init__(message)
        self.violation_type = violation_type
        self.evidence = evidence
        self.cir_code = cir_code

class PsiSyncProtocol:
    """
    Manages the ΨSync consensus protocol for shard synchronization.
    Enforces Zero-Simulation compliance for all time-based operations.
    """

    def __init__(self, certified_math: Any, cir412_handler: Any=None):
        self.math = certified_math
        self.cir412_handler = cir412_handler
        self.OUTLIER_THRESHOLD_PERCENTILE = 90
        self.MAX_OUTLIER_RATIO = 2
        self.MIN_CONSENSUS_SHARDS = 1
        self.PROGRESSIVE_DEGRADATION = True
        self.DEGRADATION_FALLBACK_MODE = 'MEDIAN'
        self.MAX_CONSENSUS_ATTEMPTS = 3
        self.CONSENSUS_TIMEOUT_MS = 5000

    def compute_global_psisync(self, shard_psisync_values: Dict[str, int], epsilon_sync: int, deterministic_timestamp: int, drv_packet_seq: Any) -> Dict[str, Any]:
        """
        Compute the global ΨSync value from shard proposals.
        """
        DeterministicTime.require_timestamp(deterministic_timestamp)
        DeterministicTime.verify_drv_packet(drv_packet_seq, deterministic_timestamp)
        if not shard_psisync_values:
            return {'global_psisync': 0, 'consensus_achieved': False, 'timestamp': deterministic_timestamp, 'timestamp_source': f'drv_packet:{drv_packet_seq}'}
        values = list(shard_psisync_values.values())
        shard_ids = list(shard_psisync_values.keys())
        outlier_result = self._detect_outliers(values, shard_ids)
        cleaned_values = outlier_result['cleaned_values']
        if not cleaned_values:
            consensus_val = 0
        else:
            consensus_val = self._compute_secure_median(cleaned_values)
        metrics = self._compute_consensus_metrics(cleaned_values, consensus_val, epsilon_sync)
        if not metrics['consensus_achieved']:
            self._handle_consensus_failure(metrics, epsilon_sync, cleaned_values)
        return {'global_psisync': consensus_val, 'consensus_achieved': metrics['consensus_achieved'], 'metrics': metrics, 'outliers': outlier_result, 'timestamp': deterministic_timestamp, 'timestamp_source': f'drv_packet:{drv_packet_seq}'}

    def _detect_outliers(self, values: List[int], shard_ids: List[str]) -> Dict[str, Any]:
        """Detect outliers using IQR method with index bounds protection."""
        if not values:
            return {'cleaned_values': [], 'outlier_shards': [], 'accepted_shards': []}
        indexed_values = [(val, idx) for idx, val in enumerate(values)]
        sorted_values = sorted(indexed_values, key=lambda x: x[0])
        max_outliers = min(len(sorted_values) // self.MAX_OUTLIER_RATIO, len(sorted_values) - len(sorted_values) * self.OUTLIER_THRESHOLD_PERCENTILE // 100)
        q1_index = len(sorted_values) // 4
        q3_index = 3 * len(sorted_values) // 4
        q1 = sorted_values[min(q1_index, len(sorted_values) - 1)][0]
        q3 = sorted_values[min(q3_index, len(sorted_values) - 1)][0]
        log_list = []
        iqr = self.math.sub(q3, q1, log_list)
        outlier_threshold = self.math.mul(iqr, 15, log_list)
        outlier_threshold = self.math.div_floor(outlier_threshold, 10, log_list)
        outlier_indices = []
        clean_values = []
        accepted_shards = []
        outlier_shards = []
        for val, idx in sorted(sorted_values):
            if len(outlier_indices) >= max_outliers:
                clean_values.append(val)
                accepted_shards.append(shard_ids[idx])
                continue
            is_outlier = val < self.math.sub(q1, outlier_threshold, log_list) or val > self.math.add(q3, outlier_threshold, log_list)
            if is_outlier:
                outlier_indices.append(idx)
                outlier_shards.append(shard_ids[idx])
            else:
                clean_values.append(val)
                accepted_shards.append(shard_ids[idx])
        return {'cleaned_values': clean_values, 'outlier_shards': outlier_shards, 'accepted_shards': accepted_shards, 'sybil_detected': False, 'outlier_detection_evidence': {'q1': q1, 'q3': q3, 'iqr': iqr, 'outlier_threshold': outlier_threshold, 'max_outliers_allowed': max_outliers, 'actual_outliers': len(outlier_indices)}}

    def _compute_secure_median(self, values: List[int]) -> int:
        """Compute median with overflow protection."""
        if not values:
            raise SecurityError('Cannot compute median of empty list', 'EMPTY_LIST', {}, 'CIR-302')
        sorted_values = sorted(values)
        n = len(sorted_values)
        try:
            if n % 2 == 1:
                return sorted_values[n // 2]
            else:
                mid1 = sorted_values[n // 2 - 1]
                mid2 = sorted_values[n // 2]
                sum_mid = self.math.add(mid1, mid2)
                return self.math.div_floor(sum_mid, 2)
        except OverflowError:
            return sorted_values[n // 2 - 1]

    def _compute_consensus_metrics(self, values: List[int], global_psisync: int, epsilon_sync: int) -> Dict[str, Any]:
        """Compute comprehensive consensus metrics with DIVISION SAFETY and quality metrics."""
        if not values:
            return {'max_deviation': 0, 'average_deviation': 0, 'consensus_achieved': False, 'consensus_quality': {'shard_agreement_ratio': 0.0, 'consensus_stability': 0, 'byzantine_resistance_score': 0}}
        deviations = []
        total_deviation = 0
        for val in sorted(values):
            deviation = self.math.abs(self.math.sub(val, global_psisync))
            deviations.append(deviation)
            total_deviation = self.math.add(total_deviation, deviation)
        max_deviation = self._max_list(deviations)
        average_deviation = self.math.div_floor(total_deviation, max(1, len(values)))
        consensus_achieved = max_deviation <= epsilon_sync
        tight_agreement_count = len([d for d in deviations if d <= epsilon_sync // 2])
        tight_agreement_count = len([d for d in deviations if d <= epsilon_sync // 2])
        shard_agreement_ratio = tight_agreement_count * 10000 // max(1, len(deviations))
        consensus_stability = self._compute_consensus_stability(values)
        byzantine_resistance_score = self._compute_byzantine_score(deviations, epsilon_sync)
        return {'max_deviation': max_deviation, 'average_deviation': average_deviation, 'consensus_achieved': consensus_achieved, 'consensus_quality': {'shard_agreement_ratio': shard_agreement_ratio, 'consensus_stability': consensus_stability, 'byzantine_resistance_score': byzantine_resistance_score}, 'deviation_distribution': {'min_deviation': self._min_list(deviations), 'max_deviation': max_deviation, 'average_deviation': average_deviation}}

    def _compute_consensus_stability(self, values: List[int]) -> int:
        """Compute consensus stability score."""
        if len(values) <= 1:
            return 1000
        bn_values = [BigNum128(v) for v in values]
        total = BigNum128(0)
        for v in sorted(bn_values):
            total = self.math.add(total, v)
        mean_val = self.math.div_floor(total, BigNum128(len(values)))
        variance = BigNum128(0)
        for v in sorted(bn_values):
            diff = self.math.sub(v, mean_val)
            squared_diff = self.math.mul(diff, diff)
            variance = self.math.add(variance, squared_diff)
        variance_int = variance.value // BigNum128.SCALE
        stability = self.math.div_floor(BigNum128(1000000), BigNum128(max(1, variance_int // 1000)))
        return min(stability.value // BigNum128.SCALE, 1000)

    def _compute_byzantine_score(self, deviations: List[int], epsilon_sync: int) -> int:
        """Compute Byzantine score from deviations with certified math."""
        if not deviations:
            return 0
        result = deviations[0]
        for val in deviations[1:]:
            result = self.math.max(result, val)
        return result

    def _min_list(self, values: List[int]) -> int:
        """Compute min of list using certified math with EMPTY LIST SAFETY."""
        if not values:
            return 0
        result = values[0]
        for val in values[1:]:
            result = self.math.min(result, val)
        return result

    def _max_list(self, values: List[int]) -> int:
        """Compute max of list using certified math with EMPTY LIST SAFETY."""
        if not values:
            return 0
        result = values[0]
        for val in values[1:]:
            result = self.math.max(result, val)
        return result

    def _compute_trimmed_mean(self, values: List[int]) -> int:
        """Compute trimmed mean as fallback consensus mechanism."""
        if len(values) <= 2:
            return self._compute_secure_median(values)
        sorted_values = sorted(values)
        trim_count = len(sorted_values) // 10
        trimmed_values = sorted_values[trim_count:len(sorted_values) - trim_count] or sorted_values
        total = sum(trimmed_values)
        return self.math.div_floor(total, max(1, len(trimmed_values)))

    def _handle_consensus_failure(self, result: Dict[str, Any], epsilon_sync: int, cleaned_values: List[int]):
        """Handle consensus failure with progressive degradation and fallback mechanisms."""
        evidence = {'consensus_result': result, 'epsilon_sync': epsilon_sync, 'max_deviation': result['max_deviation'], 'progressive_degradation': self.PROGRESSIVE_DEGRADATION, 'fallback_available': len(cleaned_values) >= self.MIN_CONSENSUS_SHARDS}
        if self.PROGRESSIVE_DEGRADATION and len(cleaned_values) >= self.MIN_CONSENSUS_SHARDS:
            fallback_consensus = self._compute_trimmed_mean(cleaned_values)
            result['fallback_consensus'] = fallback_consensus
            result['consensus_method'] = 'TRIMMED_MEAN_FALLBACK'
            if self.cir412_handler and hasattr(self.cir412_handler, 'notify'):
                self.cir412_handler.notify(reason='PSI_SYNC_CONSENSUS_DEGRADED', details=f"Max deviation {result['max_deviation']} > ε_sync {epsilon_sync}", severity='WARNING', evidence=evidence)
        elif self.cir412_handler and hasattr(self.cir412_handler, 'halt'):
            self.cir412_handler.halt(reason='PSI_SYNC_CONSENSUS_FAILURE', details=f"Max deviation {result['max_deviation']} > ε_sync {epsilon_sync}", evidence=evidence)
        else:
            raise SecurityError(f"PSI_SYNC_CONSENSUS_FAILURE: Max deviation {result['max_deviation']} > ε_sync {epsilon_sync}", violation_type='CONSENSUS_FAILURE', evidence=evidence, cir_code='CIR-412')

    def validate_shard_psisync_proposal(self, shard_id: str, proposed_psisync: int, global_psisync: int, epsilon_sync: int, previous_psisync: Optional[int]=None) -> Dict[str, Any]:
        """HARDENED: Validate individual shard ΨSync proposal."""
        validation = {'valid': True, 'violations': [], 'evidence': {'shard_id': shard_id, 'proposed_psisync': proposed_psisync, 'global_psisync': global_psisync, 'epsilon_sync': epsilon_sync}}
        deviation = self.math.abs(self.math.sub(proposed_psisync, global_psisync))
        validation['evidence']['deviation'] = deviation
        if deviation > epsilon_sync:
            validation['valid'] = False
            validation['violations'].append(f'Deviation {deviation} > ε_sync {epsilon_sync}')
        if proposed_psisync < 0:
            validation['valid'] = False
            validation['violations'].append('Negative ΨSync value')
        if proposed_psisync > 10 ** 18:
            validation['valid'] = False
            validation['violations'].append('Excessively large ΨSync value')
        if previous_psisync is not None:
            change = self.math.abs(self.math.sub(proposed_psisync, previous_psisync))
            max_allowed_change = self.math.div_floor(max(1, previous_psisync), 10)
            validation['evidence']['change_magnitude'] = change
            validation['evidence']['max_allowed_change'] = max_allowed_change
            if change > max_allowed_change:
                validation['valid'] = False
                validation['violations'].append(f'Sudden ΨSync change: {change} > {max_allowed_change}')
        return validation

def create_psisync_protocol(certified_math: Any, cir412_handler: Any=None, security_level: str='HIGH') -> PsiSyncProtocol:
    """Factory function for ΨSync protocol with security configuration."""
    protocol = PsiSyncProtocol(certified_math, cir412_handler)
    if security_level == 'PARANOID':
        protocol.OUTLIER_THRESHOLD_PERCENTILE = 80
        protocol.MAX_OUTLIER_RATIO = 4
        protocol.MIN_CONSENSUS_SHARDS = 3
        protocol.PROGRESSIVE_DEGRADATION = False
        protocol.DEGRADATION_FALLBACK_MODE = 'NONE'
    elif security_level == 'BALANCED':
        protocol.OUTLIER_THRESHOLD_PERCENTILE = 90
        protocol.MAX_OUTLIER_RATIO = 2
        protocol.MIN_CONSENSUS_SHARDS = 1
        protocol.PROGRESSIVE_DEGRADATION = True
        protocol.DEGRADATION_FALLBACK_MODE = 'MEDIAN'
    return protocol

def generate_psisync_evidence(protocol: PsiSyncProtocol, consensus_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive ΨSync evidence for Phase3EvidenceBuilder."""
    return {'psi_sync_consensus': consensus_result, 'protocol_configuration': {'outlier_threshold_percentile': protocol.OUTLIER_THRESHOLD_PERCENTILE, 'max_outlier_ratio': protocol.MAX_OUTLIER_RATIO, 'min_consensus_shards': protocol.MIN_CONSENSUS_SHARDS, 'progressive_degradation': protocol.PROGRESSIVE_DEGRADATION, 'degradation_fallback_mode': protocol.DEGRADATION_FALLBACK_MODE, 'max_consensus_attempts': protocol.MAX_CONSENSUS_ATTEMPTS, 'consensus_timeout_ms': protocol.CONSENSUS_TIMEOUT_MS}, 'security_status': {'consensus_achieved': consensus_result['consensus_achieved'], 'outlier_ratio': consensus_result['outlier_ratio'] if 'outlier_ratio' in consensus_result else 0, 'max_deviation': consensus_result['max_deviation'], 'shard_participation': 0, 'consensus_quality': consensus_result.get('consensus_quality', {}), 'fallback_used': 'fallback_consensus' in consensus_result}}
if __name__ == '__main__':
    print('PsiSyncProtocol.py is a production-perfect library module. Do not execute directly.')
    raise ZeroSimAbort(1)
__all__ = ['PsiSyncProtocol', 'SecurityError', 'create_psisync_protocol', 'generate_psisync_evidence']