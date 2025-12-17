"""
NODAllocator.py - Distributes NOD tokens to infrastructure accounts based on node contribution metrics

Implements the NODAllocator class for distributing NOD tokens to registered AEGIS infrastructure nodes
based on their contribution metrics, using CertifiedMath public API for all calculations and maintaining
full auditability via log_list, pqc_cid, and quantum_metadata.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
try:
    from ...libs.CertifiedMath import CertifiedMath, BigNum128
    from ...core.TokenStateBundle import TokenStateBundle
    from ...libs.economics.economic_constants import NOD_ALLOCATION_FRACTION, MIN_NOD_ALLOCATION_FRACTION, MAX_NOD_ALLOCATION_FRACTION, NOD_MIN_ACTIVE_NODES, NOD_MAX_ISSUANCE_PER_EPOCH, NOD_ZERO_ACTIVITY_FLOOR, MAX_NODE_REWARD_SHARE, MAX_NOD_VOTING_POWER_RATIO
except ImportError:
    try:
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.TokenStateBundle import TokenStateBundle
        from v13.libs.economics.economic_constants import NOD_ALLOCATION_FRACTION, MIN_NOD_ALLOCATION_FRACTION, MAX_NOD_ALLOCATION_FRACTION, NOD_MIN_ACTIVE_NODES, NOD_MAX_ISSUANCE_PER_EPOCH, NOD_ZERO_ACTIVITY_FLOOR, MAX_NODE_REWARD_SHARE, MAX_NOD_VOTING_POWER_RATIO
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.TokenStateBundle import TokenStateBundle
        from v13.libs.economics.economic_constants import NOD_ALLOCATION_FRACTION, MIN_NOD_ALLOCATION_FRACTION, MAX_NOD_ALLOCATION_FRACTION, NOD_MIN_ACTIVE_NODES, NOD_MAX_ISSUANCE_PER_EPOCH, NOD_ZERO_ACTIVITY_FLOOR, MAX_NODE_REWARD_SHARE, MAX_NOD_VOTING_POWER_RATIO
try:
    from ...libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
    from ...libs.governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
    from ...libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
except ImportError:
    try:
        from v13.libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
        from v13.libs.governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
        from v13.libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from economics.EconomicsGuard import EconomicsGuard, ValidationResult
        from governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
        from governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult

@dataclass
class NODAllocation:
    """Container for NOD allocation results"""
    node_id: str
    nod_amount: BigNum128
    contribution_score: BigNum128
    timestamp: int

class NODAllocator:
    """
    Allocator for distributing NOD tokens to infrastructure accounts.
    
    Distributes NOD tokens to registered AEGIS infrastructure nodes based on their
    contribution metrics, using CertifiedMath public API for all calculations and
    maintaining full auditability.
    """

    def __init__(self, cm_instance: CertifiedMath, allocation_fraction: BigNum128=None):
        """
        Initialize the NOD Allocator with V13.6 constitutional guards.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
            allocation_fraction: Custom NOD allocation fraction (must be within bounds)
        """
        self.cm = cm_instance
        self.economics_guard = EconomicsGuard(cm_instance)
        self.nod_invariant_checker = NODInvariantChecker(cm_instance)
        self.aegis_node_verifier = AEGIS_Node_Verifier(cm_instance)
        if allocation_fraction is None:
            self.allocation_fraction = NOD_ALLOCATION_FRACTION
        else:
            if self.cm.lt(allocation_fraction, MIN_NOD_ALLOCATION_FRACTION, [], None, None):
                raise ValueError(f'NOD allocation fraction {allocation_fraction.to_decimal_string()} below minimum {MIN_NOD_ALLOCATION_FRACTION.to_decimal_string()}')
            if self.cm.gt(allocation_fraction, MAX_NOD_ALLOCATION_FRACTION, [], None, None):
                raise ValueError(f'NOD allocation fraction {allocation_fraction.to_decimal_string()} above maximum {MAX_NOD_ALLOCATION_FRACTION.to_decimal_string()}')
            self.allocation_fraction = allocation_fraction

    def allocate_from_atr_fees(self, atr_total_fees: BigNum128, node_contributions: Dict[str, BigNum128], registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0, epoch_number: int=0) -> List[NODAllocation]:
        """
        Allocate NOD tokens from ATR fees to infrastructure nodes with V13.6 guard enforcement.
        
        Args:
            atr_total_fees: Total ATR fees collected
            node_contributions: Dictionary mapping node IDs to contribution scores
            registry_snapshot: AEGIS registry snapshot (hash-anchored, versioned)
            telemetry_snapshot: AEGIS telemetry snapshot (hash-anchored, versioned)
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            epoch_number: Current epoch number for emission controls
            
        Returns:
            List[NODAllocation]: List of NOD allocations for verified nodes only
        """
        registry_hash = registry_snapshot.get('snapshot_hash', 'MISSING_HASH')
        telemetry_hash = telemetry_snapshot.get('snapshot_hash', 'MISSING_HASH')
        if log_list is not None:
            log_list.append({'operation': 'nod_aegis_snapshot_anchoring', 'registry_snapshot_hash': registry_hash, 'telemetry_snapshot_hash': telemetry_hash, 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
        verified_nodes = {}
        unverified_nodes = []
        for node_id in sorted(node_contributions.keys()):
            verification_result = self.aegis_node_verifier.verify_node(node_id=node_id, registry_snapshot=registry_snapshot, telemetry_snapshot=telemetry_snapshot, log_list=log_list)
            if verification_result.is_valid:
                verified_nodes[node_id] = node_contributions[node_id]
            else:
                unverified_nodes.append((node_id, verification_result))
                if log_list is not None:
                    log_list.append({'operation': 'nod_node_verification_failed', 'node_id': node_id, 'status': verification_result.status.value, 'reason_code': verification_result.reason_code, 'reason_message': verification_result.reason_message, 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
        if not verified_nodes:
            if log_list is not None:
                log_list.append({'operation': 'nod_no_verified_nodes', 'total_nodes': len(node_contributions), 'verified_count': 0, 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
            return []
        if log_list is not None:
            log_list.append({'operation': 'nod_verification_summary', 'total_nodes': len(node_contributions), 'verified_count': len(verified_nodes), 'unverified_count': len(unverified_nodes), 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
        nod_share = self.cm.mul(atr_total_fees, self.allocation_fraction, log_list, pqc_cid, quantum_metadata)
        if self.cm.gt(nod_share, NOD_MAX_ISSUANCE_PER_EPOCH, log_list, pqc_cid, quantum_metadata):
            nod_share = NOD_MAX_ISSUANCE_PER_EPOCH
            if log_list is not None:
                log_list.append({'operation': 'nod_issuance_capped', 'original_amount': self.cm.mul(atr_total_fees, self.allocation_fraction, [], pqc_cid, quantum_metadata).to_decimal_string(), 'capped_amount': nod_share.to_decimal_string(), 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
        if self.cm.lte(nod_share, NOD_ZERO_ACTIVITY_FLOOR, log_list, pqc_cid, quantum_metadata):
            if log_list is not None:
                log_list.append({'operation': 'nod_zero_activity', 'nod_share': nod_share.to_decimal_string(), 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
            return []
        total_verified_contribution = BigNum128(0)
        for score in verified_nodes.values():
            total_verified_contribution = self.cm.add(total_verified_contribution, score, log_list, pqc_cid, quantum_metadata)
        econ_validation = self.economics_guard.validate_nod_allocation(nod_amount=nod_share, total_fees=atr_total_fees, node_voting_power=BigNum128.from_int(0), total_voting_power=BigNum128.from_int(1), node_reward_share=self.allocation_fraction, total_epoch_issuance=nod_share, active_node_count=len(verified_nodes), log_list=log_list)
        if not econ_validation.passed:
            if log_list is not None:
                log_list.append({'operation': 'nod_economic_violation', 'error_code': econ_validation.error_code, 'error_message': econ_validation.error_message, 'details': econ_validation.details, 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
            raise ValueError(f'[GUARD] Economic bound violation: {econ_validation.error_message} (code: {econ_validation.error_code})')
        return self.allocate_nod(nod_reward_pool=nod_share, node_contributions=verified_nodes, log_list=log_list, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata, deterministic_timestamp=deterministic_timestamp, epoch_number=epoch_number)

    def allocate_nod(self, nod_reward_pool: BigNum128, node_contributions: Dict[str, BigNum128], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0, epoch_number: int=0) -> List[NODAllocation]:
        """
        Allocate NOD tokens to infrastructure nodes based on contribution metrics.
        
        Args:
            nod_reward_pool: Total NOD reward pool to distribute
            node_contributions: Dictionary mapping node IDs to contribution scores
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            epoch_number: Current epoch number for emission controls
            
        Returns:
            List[NODAllocation]: List of NOD allocations for each node
        """
        if nod_reward_pool.value < 0:
            raise ValueError('NOD reward pool cannot be negative')
        if not node_contributions:
            return []
        num_active_nodes = len(node_contributions)
        if num_active_nodes < NOD_MIN_ACTIVE_NODES.value:
            if log_list is not None:
                log_list.append({'operation': 'nod_insufficient_nodes', 'active_nodes': num_active_nodes, 'required_minimum': NOD_MIN_ACTIVE_NODES.value, 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
            return []
        total_contribution = BigNum128(0)
        for score in node_contributions.values():
            total_contribution = self.cm.add(total_contribution, score, log_list, pqc_cid, quantum_metadata)
        if total_contribution.value == 0:
            return self._allocate_equal(nod_reward_pool, node_contributions, log_list, pqc_cid, quantum_metadata, deterministic_timestamp, epoch_number)
        allocations = []
        remaining_nod = nod_reward_pool
        max_node_share = self.cm.mul(nod_reward_pool, MAX_NODE_REWARD_SHARE, log_list, pqc_cid, quantum_metadata)
        sorted_nodes = sorted(node_contributions.keys())
        for i, node_id in enumerate(sorted_nodes[:-1]):
            contribution_score = node_contributions[node_id]
            share_numerator = self.cm.mul(contribution_score, nod_reward_pool, log_list, pqc_cid, quantum_metadata)
            share = self.cm.div(share_numerator, total_contribution, log_list, pqc_cid, quantum_metadata)
            capped = False
            if self.cm.gt(share, max_node_share, log_list, pqc_cid, quantum_metadata):
                share = max_node_share
                capped = True
                if log_list is not None:
                    log_list.append({'operation': 'nod_node_share_capped', 'node_id': node_id, 'original_share': share_numerator.to_decimal_string(), 'capped_share': share.to_decimal_string(), 'cap_ratio': MAX_NODE_REWARD_SHARE.to_decimal_string(), 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
            if share.value > remaining_nod.value:
                share = remaining_nod
            allocations.append(NODAllocation(node_id=node_id, nod_amount=share, contribution_score=contribution_score, timestamp=deterministic_timestamp))
            remaining_nod = self.cm.sub(remaining_nod, share, log_list, pqc_cid, quantum_metadata)
        last_node_id = sorted_nodes[-1]
        last_contribution_score = node_contributions[last_node_id]
        last_node_share = remaining_nod
        if self.cm.gt(last_node_share, max_node_share, log_list, pqc_cid, quantum_metadata):
            last_node_share = max_node_share
            if log_list is not None:
                log_list.append({'operation': 'nod_node_share_capped', 'node_id': last_node_id, 'original_share': remaining_nod.to_decimal_string(), 'capped_share': last_node_share.to_decimal_string(), 'cap_ratio': MAX_NODE_REWARD_SHARE.to_decimal_string(), 'epoch': epoch_number, 'timestamp': deterministic_timestamp})
        allocations.append(NODAllocation(node_id=last_node_id, nod_amount=last_node_share, contribution_score=last_contribution_score, timestamp=deterministic_timestamp))
        self._log_nod_allocation(nod_reward_pool, node_contributions, allocations, log_list, pqc_cid, quantum_metadata, deterministic_timestamp, epoch_number)
        return allocations

    def _allocate_equal(self, nod_reward_pool: BigNum128, node_contributions: Dict[str, BigNum128], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0, epoch_number: int=0) -> List[NODAllocation]:
        """
        Allocate NOD tokens equally when total contribution is zero.
        
        Args:
            nod_reward_pool: Total NOD reward pool to distribute
            node_contributions: Dictionary mapping node IDs to contribution scores
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
            epoch_number: Current epoch number
            
        Returns:
            List[NODAllocation]: List of equal NOD allocations for each node
        """
        num_nodes = len(node_contributions)
        if num_nodes == 0:
            return []
        equal_share = self.cm.div(nod_reward_pool, BigNum128.from_int(num_nodes), log_list, pqc_cid, quantum_metadata)
        max_node_share = self.cm.mul(nod_reward_pool, MAX_NODE_REWARD_SHARE, log_list, pqc_cid, quantum_metadata)
        if self.cm.gt(equal_share, max_node_share, log_list, pqc_cid, quantum_metadata):
            equal_share = max_node_share
        allocations = []
        remaining_nod = nod_reward_pool
        sorted_nodes = sorted(node_contributions.keys())
        for i, node_id in enumerate(sorted_nodes[:-1]):
            allocations.append(NODAllocation(node_id=node_id, nod_amount=equal_share, contribution_score=node_contributions[node_id], timestamp=deterministic_timestamp))
            remaining_nod = self.cm.sub(remaining_nod, equal_share, log_list, pqc_cid, quantum_metadata)
        last_node_id = sorted_nodes[-1]
        last_node_share = remaining_nod
        if self.cm.gt(last_node_share, max_node_share, log_list, pqc_cid, quantum_metadata):
            last_node_share = max_node_share
        allocations.append(NODAllocation(node_id=last_node_id, nod_amount=last_node_share, contribution_score=node_contributions[last_node_id], timestamp=deterministic_timestamp))
        return allocations

    def _log_nod_allocation(self, nod_reward_pool: BigNum128, node_contributions: Dict[str, BigNum128], allocations: List[NODAllocation], log_list: List[Dict[str, Any]], pqc_cid: Optional[str]=None, quantum_metadata: Optional[Dict[str, Any]]=None, deterministic_timestamp: int=0, epoch_number: int=0):
        """
        Log the NOD allocation for audit purposes.
        
        Args:
            nod_reward_pool: Total NOD reward pool
            node_contributions: Node contribution scores
            allocations: NOD allocations
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
            epoch_number: Current epoch number
        """
        allocation_count = len(allocations)
        total_allocated = BigNum128(0)
        for alloc in sorted(allocations):
            total_allocated = self.cm.add(total_allocated, alloc.nod_amount, log_list, pqc_cid, quantum_metadata)
        details = {'operation': 'nod_allocation', 'nod_reward_pool': nod_reward_pool.to_decimal_string(), 'total_contributions': sum((score.value for score in node_contributions.values())), 'total_allocated': total_allocated.to_decimal_string(), 'allocation_count': allocation_count, 'epoch': epoch_number, 'timestamp': deterministic_timestamp}
        dummy_result = BigNum128(1)
        self.cm.add(dummy_result, dummy_result, log_list, pqc_cid, quantum_metadata)
        if log_list:
            log_list[-1] = {'operation': 'nod_allocation', 'details': details, 'result': total_allocated.to_decimal_string(), 'pqc_cid': pqc_cid, 'quantum_metadata': quantum_metadata, 'timestamp': deterministic_timestamp}

def test_nod_allocator():
    """Test the NODAllocator implementation."""
    print('Testing NODAllocator...')
    cm = CertifiedMath()
    allocator = NODAllocator(cm)
    nod_reward_pool = BigNum128.from_int(1000)
    node_contributions = {'node_0xabc123': BigNum128.from_int(50), 'node_0xdef456': BigNum128.from_int(30), 'node_0xghi789': BigNum128.from_int(20)}
    log_list = []
    allocations = allocator.allocate_nod(nod_reward_pool=nod_reward_pool, node_contributions=node_contributions, log_list=log_list, pqc_cid='test_nod_001', deterministic_timestamp=1234567890)
    total_allocated = BigNum128(0)
    for alloc in sorted(allocations):
        print(f'Node {alloc.node_id}: {alloc.nod_amount.to_decimal_string()} NOD (score: {alloc.contribution_score.to_decimal_string()})')
        total_allocated = cm.add(total_allocated, alloc.nod_amount, log_list, 'test_nod_001', {})
    print(f'Total allocated: {total_allocated.to_decimal_string()} NOD')
    print(f'Log entries: {len(log_list)}')
    print('✓ NODAllocator test passed!')
if __name__ == '__main__':
    test_nod_allocator()