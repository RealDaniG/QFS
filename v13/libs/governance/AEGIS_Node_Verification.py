"""
AEGIS_Node_Verification.py - Pure Deterministic Node Verification Library

Implements deterministic verification of AEGIS infrastructure nodes based on
pre-fetched telemetry snapshots. This is a pure function library with NO network
I/O - all inputs must be provided as versioned, hash-anchored snapshots.

Verification Criteria (all must pass):
1. Registry entry exists and is not revoked
2. PQC public key present and signature scheme supported (Dilithium5)
3. Uptime meets minimum threshold
4. Telemetry hashes well-formed and coherent (no conflicts)
5. Node health metrics above policy thresholds

This module enforces NOD-I2 (verified nodes only) and is called by:
- NODAllocator (filter eligible nodes before allocation)
- InfrastructureGovernance (reject proposals/votes from unverified nodes)
- StateTransitionEngine (NOD deltas only for verified nodes)

CRITICAL: This is a blocking dependency for NOD-I2 invariant closure.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
try:
    from ..CertifiedMath import BigNum128, CertifiedMath
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from CertifiedMath import BigNum128, CertifiedMath

class NodeVerificationStatus(Enum):
    """Enumeration of node verification outcomes."""
    VERIFIED = 'VERIFIED'
    UNVERIFIED_NO_REGISTRY_ENTRY = 'UNVERIFIED_NO_REGISTRY_ENTRY'
    UNVERIFIED_REVOKED = 'UNVERIFIED_REVOKED'
    UNVERIFIED_NO_PQC_KEY = 'UNVERIFIED_NO_PQC_KEY'
    UNVERIFIED_UNSUPPORTED_PQC_SCHEME = 'UNVERIFIED_UNSUPPORTED_PQC_SCHEME'
    UNVERIFIED_LOW_UPTIME = 'UNVERIFIED_LOW_UPTIME'
    UNVERIFIED_UNHEALTHY = 'UNVERIFIED_UNHEALTHY'
    UNVERIFIED_TELEMETRY_HASH_CONFLICT = 'UNVERIFIED_TELEMETRY_HASH_CONFLICT'
    UNVERIFIED_TELEMETRY_MALFORMED = 'UNVERIFIED_TELEMETRY_MALFORMED'

@dataclass
class NodeVerificationResult:
    """Result of node verification check."""
    node_id: str
    is_valid: bool
    status: NodeVerificationStatus
    reason_code: Optional[str] = None
    reason_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

    @property
    def metrics_str(self) -> str:
        """Backward compatibility: Return deterministic JSON string of metrics."""
        return json.dumps(self.metrics or {}, sort_keys=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {'node_id': self.node_id, 'is_valid': self.is_valid, 'status': self.status.value, 'reason_code': self.reason_code, 'reason_message': self.reason_message, 'metrics': self.metrics or {}}

class NodeVerificationPolicy:
    """Constitutional policy thresholds for node verification."""
    MIN_UPTIME_RATIO = BigNum128.from_string('0.90')
    SUPPORTED_PQC_SCHEMES = {'Dilithium5', 'Dilithium3', 'Dilithium2'}
    MIN_HEALTH_SCORE = BigNum128.from_string('0.75')
    REQUIRED_TELEMETRY_SCHEMA_VERSION = 'v1.0'

class AEGIS_Node_Verifier:
    """
    Pure, deterministic node verification library.
    
    NO network I/O - all inputs are pre-fetched, versioned snapshots.
    All verification logic is pure functions for deterministic replay.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the AEGIS Node Verifier.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic comparisons
        """
        self.cm = cm_instance

    def verify_node(self, node_id: str, registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], log_list: Optional[List[Dict[str, Any]]]=None) -> NodeVerificationResult:
        """
        Verify a node against registry and telemetry snapshots.
        
        This is the primary entry point for node verification.
        All checks are performed in deterministic order.
        
        Args:
            node_id: Node identifier to verify
            registry_snapshot: Pre-fetched AEGIS registry snapshot (versioned, hash-anchored)
            telemetry_snapshot: Pre-fetched AEGIS telemetry snapshot (versioned, hash-anchored)
            log_list: Optional log list for audit trail
            
        Returns:
            NodeVerificationResult with verification status and details
        """
        if log_list is None:
            log_list = []
        registry_result = self._check_registry_entry(node_id, registry_snapshot)
        if not registry_result.is_valid:
            return registry_result
        pqc_result = self._check_pqc_key(node_id, registry_snapshot)
        if not pqc_result.is_valid:
            return pqc_result
        uptime_result = self._check_uptime(node_id, telemetry_snapshot)
        if not uptime_result.is_valid:
            return uptime_result
        health_result = self._check_health(node_id, telemetry_snapshot)
        if not health_result.is_valid:
            return health_result
        telemetry_result = self._check_telemetry_coherence(node_id, telemetry_snapshot)
        if not telemetry_result.is_valid:
            return telemetry_result
        return NodeVerificationResult(node_id=node_id, is_valid=True, status=NodeVerificationStatus.VERIFIED, metrics={'uptime_ratio': telemetry_snapshot.get('nodes', {}).get(node_id, {}).get('uptime_ratio', 'unknown'), 'health_score': telemetry_snapshot.get('nodes', {}).get(node_id, {}).get('health_score', 'unknown'), 'pqc_scheme': registry_snapshot.get('nodes', {}).get(node_id, {}).get('pqc_scheme', 'unknown')})

    def _check_registry_entry(self, node_id: str, registry_snapshot: Dict[str, Any]) -> NodeVerificationResult:
        """
        Check if node has valid registry entry.
        
        Validates:
        - Entry exists in registry
        - Entry is not revoked
        
        Args:
            node_id: Node identifier
            registry_snapshot: Registry snapshot
            
        Returns:
            NodeVerificationResult
        """
        if 'nodes' not in registry_snapshot:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_NO_REGISTRY_ENTRY, reason_code='REGISTRY_SNAPSHOT_MALFORMED', reason_message="Registry snapshot missing 'nodes' field")
        if node_id not in registry_snapshot['nodes']:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_NO_REGISTRY_ENTRY, reason_code='NODE_NOT_IN_REGISTRY', reason_message=f'Node {node_id} not found in AEGIS registry')
        node_entry = registry_snapshot['nodes'][node_id]
        if node_entry.get('revoked', False):
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_REVOKED, reason_code='NODE_REVOKED', reason_message=f'Node {node_id} is revoked in AEGIS registry', metrics={'revocation_reason': node_entry.get('revocation_reason', 'unknown')})
        return NodeVerificationResult(node_id=node_id, is_valid=True, status=NodeVerificationStatus.VERIFIED)

    def _check_pqc_key(self, node_id: str, registry_snapshot: Dict[str, Any]) -> NodeVerificationResult:
        """
        Check if node has valid PQC key and supported scheme.
        
        Validates:
        - PQC public key present
        - PQC scheme supported (Dilithium5, Dilithium3, Dilithium2)
        
        Args:
            node_id: Node identifier
            registry_snapshot: Registry snapshot
            
        Returns:
            NodeVerificationResult
        """
        node_entry = registry_snapshot['nodes'][node_id]
        if 'pqc_public_key' not in node_entry or not node_entry['pqc_public_key']:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_NO_PQC_KEY, reason_code='PQC_KEY_MISSING', reason_message=f'Node {node_id} missing PQC public key')
        pqc_scheme = node_entry.get('pqc_scheme', '')
        if pqc_scheme not in NodeVerificationPolicy.SUPPORTED_PQC_SCHEMES:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_UNSUPPORTED_PQC_SCHEME, reason_code='PQC_SCHEME_UNSUPPORTED', reason_message=f"Node {node_id} PQC scheme '{pqc_scheme}' not supported", metrics={'pqc_scheme': pqc_scheme, 'supported_schemes': list(NodeVerificationPolicy.SUPPORTED_PQC_SCHEMES)})
        return NodeVerificationResult(node_id=node_id, is_valid=True, status=NodeVerificationStatus.VERIFIED)

    def _check_uptime(self, node_id: str, telemetry_snapshot: Dict[str, Any]) -> NodeVerificationResult:
        """
        Check if node uptime meets minimum threshold.
        
        Validates:
        - Uptime ratio >= MIN_UPTIME_RATIO (90%)
        
        Args:
            node_id: Node identifier
            telemetry_snapshot: Telemetry snapshot
            
        Returns:
            NodeVerificationResult
        """
        if 'nodes' not in telemetry_snapshot:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_TELEMETRY_MALFORMED, reason_code='TELEMETRY_SNAPSHOT_MALFORMED', reason_message="Telemetry snapshot missing 'nodes' field")
        if node_id not in telemetry_snapshot['nodes']:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_TELEMETRY_MALFORMED, reason_code='NODE_NOT_IN_TELEMETRY', reason_message=f'Node {node_id} not found in telemetry snapshot')
        node_telemetry = telemetry_snapshot['nodes'][node_id]
        if 'uptime_ratio' not in node_telemetry:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_TELEMETRY_MALFORMED, reason_code='UPTIME_RATIO_MISSING', reason_message=f'Node {node_id} telemetry missing uptime_ratio')
        uptime_ratio = BigNum128.from_string(str(node_telemetry['uptime_ratio']))
        if self.cm.lt(uptime_ratio, NodeVerificationPolicy.MIN_UPTIME_RATIO, []):
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_LOW_UPTIME, reason_code='UPTIME_BELOW_THRESHOLD', reason_message=f'Node {node_id} uptime {uptime_ratio.to_decimal_string()} below minimum {NodeVerificationPolicy.MIN_UPTIME_RATIO.to_decimal_string()}', metrics={'uptime_ratio': uptime_ratio.to_decimal_string(), 'min_required': NodeVerificationPolicy.MIN_UPTIME_RATIO.to_decimal_string()})
        return NodeVerificationResult(node_id=node_id, is_valid=True, status=NodeVerificationStatus.VERIFIED)

    def _check_health(self, node_id: str, telemetry_snapshot: Dict[str, Any]) -> NodeVerificationResult:
        """
        Check if node health score meets minimum threshold.
        
        Validates:
        - Health score >= MIN_HEALTH_SCORE (75%)
        
        Args:
            node_id: Node identifier
            telemetry_snapshot: Telemetry snapshot
            
        Returns:
            NodeVerificationResult
        """
        node_telemetry = telemetry_snapshot['nodes'][node_id]
        if 'health_score' not in node_telemetry:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_TELEMETRY_MALFORMED, reason_code='HEALTH_SCORE_MISSING', reason_message=f'Node {node_id} telemetry missing health_score')
        health_score = BigNum128.from_string(str(node_telemetry['health_score']))
        if self.cm.lt(health_score, NodeVerificationPolicy.MIN_HEALTH_SCORE, []):
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_UNHEALTHY, reason_code='HEALTH_BELOW_THRESHOLD', reason_message=f'Node {node_id} health {health_score.to_decimal_string()} below minimum {NodeVerificationPolicy.MIN_HEALTH_SCORE.to_decimal_string()}', metrics={'health_score': health_score.to_decimal_string(), 'min_required': NodeVerificationPolicy.MIN_HEALTH_SCORE.to_decimal_string()})
        return NodeVerificationResult(node_id=node_id, is_valid=True, status=NodeVerificationStatus.VERIFIED)

    def _check_telemetry_coherence(self, node_id: str, telemetry_snapshot: Dict[str, Any]) -> NodeVerificationResult:
        """
        Check if telemetry data is well-formed and coherent.
        
        Validates:
        - Schema version matches required version
        - Telemetry hash present and well-formed (64-char SHA-256)
        - No conflicting entries
        
        Args:
            node_id: Node identifier
            telemetry_snapshot: Telemetry snapshot
            
        Returns:
            NodeVerificationResult
        """
        schema_version = telemetry_snapshot.get('schema_version', '')
        if schema_version != NodeVerificationPolicy.REQUIRED_TELEMETRY_SCHEMA_VERSION:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_TELEMETRY_MALFORMED, reason_code='TELEMETRY_SCHEMA_VERSION_MISMATCH', reason_message=f"Telemetry schema version '{schema_version}' does not match required '{NodeVerificationPolicy.REQUIRED_TELEMETRY_SCHEMA_VERSION}'", metrics={'schema_version': schema_version, 'required_version': NodeVerificationPolicy.REQUIRED_TELEMETRY_SCHEMA_VERSION})
        telemetry_hash = telemetry_snapshot.get('telemetry_hash', '')
        if not telemetry_hash or len(telemetry_hash) != 64:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_TELEMETRY_MALFORMED, reason_code='TELEMETRY_HASH_INVALID', reason_message=f'Telemetry hash invalid (expected 64-char SHA-256, got {len(telemetry_hash)} chars)', metrics={'telemetry_hash': telemetry_hash})
        node_telemetry = telemetry_snapshot['nodes'][node_id]
        if 'conflict_detected' in node_telemetry and node_telemetry['conflict_detected']:
            return NodeVerificationResult(node_id=node_id, is_valid=False, status=NodeVerificationStatus.UNVERIFIED_TELEMETRY_HASH_CONFLICT, reason_code='TELEMETRY_CONFLICT_DETECTED', reason_message=f'Node {node_id} has conflicting telemetry entries', metrics={'conflict_reason': node_telemetry.get('conflict_reason', 'unknown')})
        return NodeVerificationResult(node_id=node_id, is_valid=True, status=NodeVerificationStatus.VERIFIED)

    def verify_nodes_batch(self, node_ids: List[str], registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], log_list: Optional[List[Dict[str, Any]]]=None) -> Dict[str, NodeVerificationResult]:
        """
        Verify multiple nodes in a single call.
        
        Processes nodes in deterministic sorted order.
        
        Args:
            node_ids: List of node identifiers to verify
            registry_snapshot: Pre-fetched AEGIS registry snapshot
            telemetry_snapshot: Pre-fetched AEGIS telemetry snapshot
            log_list: Optional log list for audit trail
            
        Returns:
            Dict mapping node_id to NodeVerificationResult
        """
        if log_list is None:
            log_list = []
        results = {}
        sorted_node_ids = sorted(node_ids)
        for node_id in sorted_node_ids:
            results[node_id] = self.verify_node(node_id, registry_snapshot, telemetry_snapshot, log_list)
        return results

def test_aegis_node_verification():
    """
    Test the AEGIS_Node_Verifier implementation with comprehensive scenarios.
    """
    print('\n=== Testing AEGIS_Node_Verifier - Pure Deterministic Verification ===')
    cm = CertifiedMath()
    verifier = AEGIS_Node_Verifier(cm)
    registry_snapshot = {'schema_version': 'v1.0', 'nodes': {'node_valid': {'pqc_public_key': '0x1234567890abcdef', 'pqc_scheme': 'Dilithium5', 'revoked': False}, 'node_revoked': {'pqc_public_key': '0xabcdef123456', 'pqc_scheme': 'Dilithium5', 'revoked': True, 'revocation_reason': 'Security violation'}, 'node_no_pqc': {'pqc_public_key': '', 'pqc_scheme': '', 'revoked': False}, 'node_bad_scheme': {'pqc_public_key': '0xfedcba987654', 'pqc_scheme': 'RSA2048', 'revoked': False}}}
    telemetry_snapshot = {'schema_version': 'v1.0', 'telemetry_hash': 'a' * 64, 'block_height': 12345, 'nodes': {'node_valid': {'uptime_ratio': '0.95', 'health_score': '0.80', 'conflict_detected': False}, 'node_low_uptime': {'uptime_ratio': '0.85', 'health_score': '0.80', 'conflict_detected': False}, 'node_unhealthy': {'uptime_ratio': '0.95', 'health_score': '0.70', 'conflict_detected': False}, 'node_conflict': {'uptime_ratio': '0.95', 'health_score': '0.80', 'conflict_detected': True, 'conflict_reason': 'Duplicate entries in different shards'}}}
    print('\n--- Scenario 1: Valid Node (All Checks Pass) ---')
    result = verifier.verify_node('node_valid', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_valid')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    assert result.is_valid == True, 'Valid node should pass all checks'
    assert result.status == NodeVerificationStatus.VERIFIED
    print('\n--- Scenario 2: Node Not in Registry ---')
    result = verifier.verify_node('node_nonexistent', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_nonexistent')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    print(f'Reason: {result.reason_message}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_NO_REGISTRY_ENTRY
    print('\n--- Scenario 3: Revoked Node ---')
    telemetry_snapshot['nodes']['node_revoked'] = {'uptime_ratio': '0.95', 'health_score': '0.80', 'conflict_detected': False}
    result = verifier.verify_node('node_revoked', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_revoked')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    print(f'Reason: {result.reason_message}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_REVOKED
    print('\n--- Scenario 4: Node Missing PQC Key ---')
    telemetry_snapshot['nodes']['node_no_pqc'] = {'uptime_ratio': '0.95', 'health_score': '0.80', 'conflict_detected': False}
    result = verifier.verify_node('node_no_pqc', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_no_pqc')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    print(f'Reason: {result.reason_message}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_NO_PQC_KEY
    print('\n--- Scenario 5: Unsupported PQC Scheme ---')
    telemetry_snapshot['nodes']['node_bad_scheme'] = {'uptime_ratio': '0.95', 'health_score': '0.80', 'conflict_detected': False}
    result = verifier.verify_node('node_bad_scheme', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_bad_scheme')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    print(f'Reason: {result.reason_message}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_UNSUPPORTED_PQC_SCHEME
    print('\n--- Scenario 6: Low Uptime ---')
    registry_snapshot['nodes']['node_low_uptime'] = {'pqc_public_key': '0x11111111', 'pqc_scheme': 'Dilithium5', 'revoked': False}
    result = verifier.verify_node('node_low_uptime', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_low_uptime')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    print(f'Reason: {result.reason_message}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_LOW_UPTIME
    print('\n--- Scenario 7: Unhealthy Node ---')
    registry_snapshot['nodes']['node_unhealthy'] = {'pqc_public_key': '0x22222222', 'pqc_scheme': 'Dilithium5', 'revoked': False}
    result = verifier.verify_node('node_unhealthy', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_unhealthy')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    print(f'Reason: {result.reason_message}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_UNHEALTHY
    print('\n--- Scenario 8: Telemetry Hash Conflict ---')
    registry_snapshot['nodes']['node_conflict'] = {'pqc_public_key': '0x33333333', 'pqc_scheme': 'Dilithium5', 'revoked': False}
    result = verifier.verify_node('node_conflict', registry_snapshot, telemetry_snapshot)
    print(f'Node: node_conflict')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    print(f'Reason: {result.reason_message}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_TELEMETRY_HASH_CONFLICT
    print('\n--- Scenario 9: Batch Verification ---')
    node_ids = ['node_valid', 'node_revoked', 'node_low_uptime']
    results = verifier.verify_nodes_batch(node_ids, registry_snapshot, telemetry_snapshot)
    print(f'Batch verification of {len(node_ids)} nodes:')
    for node_id, result in results.items():
        print(f'  {node_id}: {result.status.value} (valid={result.is_valid})')
    assert len(results) == 3
    assert results['node_valid'].is_valid == True
    assert results['node_revoked'].is_valid == False
    assert results['node_low_uptime'].is_valid == False
    print('\n--- Scenario 10: Malformed Telemetry Snapshot ---')
    bad_telemetry = {'schema_version': 'v0.9'}
    result = verifier.verify_node('node_valid', registry_snapshot, bad_telemetry)
    print(f'Malformed telemetry check:')
    print(f'Is valid: {result.is_valid}')
    print(f'Status: {result.status.value}')
    assert result.is_valid == False
    assert result.status == NodeVerificationStatus.UNVERIFIED_TELEMETRY_MALFORMED
    print('\n✅ All 10 AEGIS_Node_Verifier scenarios passed!')
    print('\n=== AEGIS_Node_Verification.py is QFS V13.6 Compliant ===')
if __name__ == '__main__':
    test_aegis_node_verification()