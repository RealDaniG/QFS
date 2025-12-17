from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
from libs.fatal_errors import ZeroSimAbort, EconomicInvariantBreach, GovernanceGuardFailure
from typing import Any, Dict, List, Optional, Set
from v13.libs.DeterministicTime import DeterministicTime

class RecoverySecurityError(Exception):
    """Custom exception for recovery security violations."""

    def __init__(self, message, violation_type, evidence, cir_code):
        super().__init__(message)
        self.violation_type = violation_type
        self.evidence = evidence
        self.cir_code = cir_code

class SystemRecoveryProtocol:
    """
    Manages system recovery, safe mode, and governance intervention.
    Enforces Zero-Simulation compliance for all time-based operations.
    """

    def __init__(self, certified_math: Any, pqc_verifier: Any, founding_nodes: Dict[str, Any], recovery_threshold: int):
        self.math = certified_math
        self.pqc_verifier = pqc_verifier
        self.founding_nodes = founding_nodes
        self.recovery_threshold = recovery_threshold
        self.current_state = 'NORMAL'
        self.safe_mode_activated = False
        self.safe_mode_start_time = 0
        self.recovery_history = []
        self.recovery_attempt_count = 0
        self.max_recovery_attempts = 20
        self.SAFE_MODE_TIMEOUT = 7200
        self.RECOVERY_COMMAND_EXPIRY = 600
        self._suspicious_node_threshold = 5
        self.isolated_shards = set()
        self.halted_shards = set()
        self.state_checkpoints = {}
        self.recovery_health_score = 100
        self._economic_activity_frozen = False
        self._economic_activity_frozen = False
        self.recovery_progress = 0
        self._phase3_components = {}
        self.MIN_FOUNDING_NODES_ACTIVE = 3

    def trigger_recovery(self, reason: str, evidence: Dict[str, Any], deterministic_timestamp: int, drv_packet_seq: Any) -> Dict[str, Any]:
        """
        Trigger a system recovery event.
        """
        self._notify_components_of_recovery_state()
        return True

    def _detect_byzantine_founding_nodes(self, evidence_chain: List[Dict]) -> List[str]:
        """Detect potentially byzantine nodes based on evidence."""
        return []

    def get_recovery_status(self, deterministic_timestamp: int, drv_packet_seq: Any) -> Dict[str, Any]:
        """
        Get comprehensive recovery status.
        """
        DeterministicTime.require_timestamp(deterministic_timestamp)
        DeterministicTime.verify_drv_packet(drv_packet_seq, deterministic_timestamp)
        safe_mode_duration = 0
        if self.safe_mode_activated:
            safe_mode_duration = deterministic_timestamp - self.safe_mode_start_time
        safe_mode_timeout_exceeded = safe_mode_duration > self.SAFE_MODE_TIMEOUT
        evidence_chain = self.recovery_history[-10:] if self.recovery_history else []
        return {'current_state': self.current_state, 'safe_mode_activated': self.safe_mode_activated, 'safe_mode_duration': safe_mode_duration, 'safe_mode_timeout_exceeded': safe_mode_timeout_exceeded, 'safe_mode_timeout': self.SAFE_MODE_TIMEOUT, 'isolated_shards': list(self.isolated_shards), 'halted_shards': list(self.halted_shards), 'recovery_history_length': len(self.recovery_history), 'recovery_attempt_count': self.recovery_attempt_count, 'max_recovery_attempts': self.max_recovery_attempts, 'founding_nodes': {'total': len(self.founding_nodes), 'recovery_threshold': self.recovery_threshold, 'min_required': self.MIN_FOUNDING_NODES_ACTIVE, 'byzantine_nodes_detected': len(self._detect_byzantine_founding_nodes([]))}, 'checkpoints_available': list(self.state_checkpoints.keys()), 'recovery_health_score': self.recovery_health_score, 'economic_activity_frozen': self._economic_activity_frozen, 'recovery_progress': self.recovery_progress, 'recovery_evidence_chain': evidence_chain, 'timestamp_check': {'current_time': deterministic_timestamp, 'source': f'drv_packet:{drv_packet_seq}'}}

    def integrate_with_phase3_components(self, psi_field_engine: Any=None, harmonic_economics: Any=None, treasury_engine: Any=None, psisync_protocol: Any=None):
        """
        Integrate recovery protocol with Phase 3 components for coordinated response.
        """
        self._phase3_components = {'psi_field_engine': psi_field_engine, 'harmonic_economics': harmonic_economics, 'treasury_engine': treasury_engine, 'psisync_protocol': psisync_protocol}
        self._notify_components_of_recovery_state()

    def _notify_components_of_recovery_state(self):
        """Notify all Phase 3 components of current recovery state."""
        for component_name, component in self._phase3_components.items():
            if component and hasattr(component, 'set_recovery_state'):
                try:
                    component.set_recovery_state(self.current_state, self.safe_mode_activated)
                except Exception:
                    pass

def create_system_recovery_protocol(certified_math: Any, pqc_verifier: Any, founding_nodes: Dict[str, Any], recovery_threshold: int, security_level: str='HIGH') -> SystemRecoveryProtocol:
    """
    Factory function for system recovery protocol with security configuration.
    """
    protocol = SystemRecoveryProtocol(certified_math, pqc_verifier, founding_nodes, recovery_threshold)
    if security_level == 'PARANOID':
        protocol.max_recovery_attempts = 5
        protocol.SAFE_MODE_TIMEOUT = 1800
        protocol.RECOVERY_COMMAND_EXPIRY = 120
        protocol._suspicious_node_threshold = 2
    elif security_level == 'BALANCED':
        protocol.max_recovery_attempts = 20
        protocol.SAFE_MODE_TIMEOUT = 7200
        protocol.RECOVERY_COMMAND_EXPIRY = 600
        protocol._suspicious_node_threshold = 5
    return protocol

def validate_safe_mode_state(protocol: SystemRecoveryProtocol, deterministic_timestamp: int) -> bool:
    """
    Validate that safe mode state is consistent and secure.
    """
    DeterministicTime.require_timestamp(deterministic_timestamp)
    if protocol.safe_mode_activated:
        duration = deterministic_timestamp - protocol.safe_mode_start_time
        return duration <= protocol.SAFE_MODE_TIMEOUT
    return True
if __name__ == '__main__':
    raise ZeroSimAbort(1)
__all__ = ['SystemRecoveryProtocol', 'RecoverySecurityError', 'create_system_recovery_protocol', 'validate_safe_mode_state']