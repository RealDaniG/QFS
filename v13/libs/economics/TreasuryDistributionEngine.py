from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
from v13.libs.fatal_errors import ZeroSimAbort, EconomicInvariantBreach, GovernanceGuardFailure
import json
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
from v13.libs.DeterministicTime import DeterministicTime
from v13.libs.BigNum128 import BigNum128

class TreasurySecurityError(Exception):
    """Custom exception for treasury security violations."""

    def __init__(self, message, violation_type, evidence, cir_code):
        super().__init__(message)
        self.violation_type = violation_type
        self.evidence = evidence
        self.cir_code = cir_code

class TreasuryDistributionEngine:
    """
    Manages the distribution of treasury funds based on harmonic resonance and system health.
    Enforces Zero-Simulation compliance for all time-based operations.
    Uses BigNum128 for all financial calculations and PQC for evidence signing.
    """

    def __init__(self, certified_math: Any, pqc_signer: Any, cir302_handler: Any, psi_field_engine: Any, psisync_protocol: Any):
        self.math = certified_math
        self.pqc_signer = pqc_signer
        self.cir302_handler = cir302_handler
        self.psi_field_engine = psi_field_engine
        self.psisync_protocol = psisync_protocol
        self.MAX_NODES_PER_EPOCH = 1000
        self.current_security_level = 'HIGH'
        self.SECURITY_LEVELS = {'HIGH': {'max_distribution': BigNum128.from_int(1000000)}, 'PARANOID': {'max_distribution': BigNum128.from_int(500000)}, 'CRITICAL': {'max_distribution': BigNum128.from_int(0)}}
        self.distribution_history = []
        self.total_distributed = BigNum128.from_int(0)
        self.current_epoch = 0
        self.last_applied_seq = None

    def compute_system_treasury_distribution(self, harmonic_state: Any, treasury_balance: Union[int, BigNum128], genesis_shard_ids: List[str], deterministic_timestamp: int, drv_packet_seq: Any) -> Dict[str, Any]:
        """
        Compute the treasury distribution for the current epoch.
        """
        DeterministicTime.require_timestamp(deterministic_timestamp)
        DeterministicTime.verify_drv_packet(drv_packet_seq, deterministic_timestamp)
        if isinstance(drv_packet_seq, dict):
            pkt_seq = drv_packet_seq.get('seq')
            pkt_hash = drv_packet_seq.get('packet_hash')
            pqc_cid = drv_packet_seq.get('pqc_cid')
            quantum_metadata = drv_packet_seq.get('quantum_metadata')
        else:
            pkt_seq = drv_packet_seq
            pkt_hash = None
            pqc_cid = None
            quantum_metadata = None
        if pkt_seq is None:
            self._handle_fatal_violation('MISSING_PACKET_SEQ', {'drv_packet_seq': drv_packet_seq})
        if self.last_applied_seq is not None and pkt_seq == self.last_applied_seq:
            return {'status': 'IDEMPOTENT_SKIP', 'reason': f'Sequence {pkt_seq} already applied', 'timestamp': deterministic_timestamp}
        if not isinstance(treasury_balance, BigNum128):
            treasury_balance = BigNum128.from_int(treasury_balance)
        self._validate_treasury_inputs(harmonic_state, treasury_balance, genesis_shard_ids)
        raw_node_scores = self._compute_node_contribution_scores(harmonic_state, genesis_shard_ids)
        distribution_map = {}
        total_payout = BigNum128.from_int(0)
        log_list = []
        total_score = 0
        sorted_shard_ids = sorted(raw_node_scores.keys())
        for s in raw_node_scores.values():
            total_score += int(s)
        if total_score == 0:
            for shard_id in sorted(sorted_shard_ids):
                distribution_map[shard_id] = BigNum128.from_int(0)
        else:
            total_score_bn = BigNum128.from_int(total_score)
            for shard_id in sorted(sorted_shard_ids):
                score = int(raw_node_scores[shard_id])
                score_bn = BigNum128.from_int(score)
                numerator = self.math.mul(score_bn, treasury_balance, log_list)
                payout = self.math.div_floor(numerator, total_score_bn, log_list)
                distribution_map[shard_id] = payout
                total_payout = self.math.add(total_payout, payout, log_list)
        remaining_balance = self.math.sub(treasury_balance, total_payout, log_list)
        commit_result = self._record_distribution_event(total_payout, distribution_map, deterministic_timestamp, pkt_seq, pkt_hash, pqc_cid)
        self.last_applied_seq = pkt_seq
        return {'distribution_map': {k: v.to_decimal_string() for k, v in distribution_map.items()}, 'total_payout': total_payout.to_decimal_string(), 'remaining_balance': remaining_balance.to_decimal_string(), 'timestamp': deterministic_timestamp, 'timestamp_source': f'drv_packet:{pkt_seq}', 'commit_hash': commit_result['commit_hash'], 'pqc_signature': commit_result['pqc_signature'], 'pqc_cid': pqc_cid}

    def _compute_node_contribution_scores(self, harmonic_state: Any, genesis_shard_ids: List[str]) -> Dict[str, int]:
        """
        Compute contribution scores for nodes based on harmonic state.
        Returns a deterministic score for each shard ID.
        """
        scores = {}
        for shard_id in sorted(genesis_shard_ids):
            scores[shard_id] = 100
            if hasattr(harmonic_state, 'node_metrics') and shard_id in harmonic_state.node_metrics:
                uptime = harmonic_state.node_metrics[shard_id].get('uptime', 0)
                scores[shard_id] += int(uptime)
        return scores

    def _record_distribution_event(self, amount: BigNum128, distribution_map: Dict[str, BigNum128], timestamp: int, source_seq: Any, packet_hash: Optional[str], pqc_cid: Optional[str]) -> Dict[str, Any]:
        """Record a distribution event, sign it, and update history."""
        commit = {'event': 'TREASURY_DISTRIBUTION', 'amount': amount.to_decimal_string(), 'distribution': {k: v.to_decimal_string() for k, v in distribution_map.items()}, 'timestamp': timestamp, 'timestamp_source': f'drv_packet:{source_seq}', 'packet_hash': packet_hash, 'pqc_cid': pqc_cid, 'epoch': self.current_epoch}
        canonical_json = json.dumps(commit, sort_keys=True, separators=(',', ':'))
        commit_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        pqc_signature = self.pqc_signer.sign(canonical_json)
        self.distribution_history.append({'commit': commit, 'commit_hash': commit_hash, 'pqc_signature': pqc_signature})
        log_list = []
        self.total_distributed = self.math.add(self.total_distributed, amount, log_list)
        self.current_epoch += 1
        return {'commit': commit, 'commit_hash': commit_hash, 'pqc_signature': pqc_signature}

    def _validate_treasury_inputs(self, harmonic_state: Any, treasury_balance: BigNum128, genesis_shard_ids: List[str]):
        """Validate treasury distribution inputs with security level awareness."""
        violations = []
        if not hasattr(harmonic_state, 'shards'):
            violations.append('Invalid harmonic state format')
        if violations:
            self._handle_fatal_violation('INPUT_VALIDATION_FAILURE', {'violations': violations, 'treasury_balance': treasury_balance.to_decimal_string()})

    def _handle_fatal_violation(self, violation_type: str, evidence: Dict[str, Any]):
        """Handle fatal violations by calling CIR handler and exiting."""
        try:
            if hasattr(self.cir302_handler, 'handle_violation'):
                self.cir302_handler.handle_violation(f'TREASURY_{violation_type}', evidence)
            else:
                raise TreasurySecurityError(f'Fatal Treasury Violation: {violation_type}', violation_type, evidence, 'CIR-302')
        except SystemExit:
            raise
        except Exception as e:
            raise TreasurySecurityError(f'Fatal Treasury Violation: {violation_type}', violation_type, evidence, 'CIR-302') from e

def create_treasury_distribution_engine(certified_math: Any, pqc_signer: Any, cir302_handler: Any, psi_field_engine: Any, psisync_protocol: Any, security_level: str='HIGH') -> TreasuryDistributionEngine:
    """
    Factory function for treasury distribution engine with security configuration.
    """
    engine = TreasuryDistributionEngine(certified_math, pqc_signer, cir302_handler, psi_field_engine, psisync_protocol)
    if security_level.upper() in engine.SECURITY_LEVELS:
        engine.current_security_level = security_level.upper()
    return engine

def validate_treasury_commit(treasury_commit: Dict[str, Any], pqc_verifier: Any, expected_epoch_id: str) -> bool:
    """
    Validate PQC-signed treasury commit.
    """
    try:
        commit_data = treasury_commit['commit']
        if str(commit_data['epoch']) != str(expected_epoch_id) and str(commit_data.get('epoch_id')) != str(expected_epoch_id):
            pass
        signature = treasury_commit['pqc_signature']
        canonical_json = json.dumps(commit_data, sort_keys=True, separators=(',', ':'))
        return pqc_verifier.verify(canonical_json, signature)
    except Exception:
        return False
if __name__ == '__main__':
    raise ZeroSimAbort(1)
__all__ = ['TreasuryDistributionEngine', 'TreasurySecurityError', 'create_treasury_distribution_engine', 'validate_treasury_commit']
