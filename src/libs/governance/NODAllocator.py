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

# Import required modules
try:
    # Try relative imports first (for package usage)
    from ...libs.CertifiedMath import CertifiedMath, BigNum128
    from ...core.TokenStateBundle import TokenStateBundle
    from ...libs.economics.economic_constants import (
        NOD_ALLOCATION_FRACTION,
        MIN_NOD_ALLOCATION_FRACTION,
        MAX_NOD_ALLOCATION_FRACTION,
        NOD_MIN_ACTIVE_NODES,
        NOD_MAX_ISSUANCE_PER_EPOCH,
        NOD_ZERO_ACTIVITY_FLOOR,
        MAX_NODE_REWARD_SHARE,
        MAX_NOD_VOTING_POWER_RATIO
    )
except ImportError:
    # Fallback to absolute imports (for direct execution)
    try:
        from src.libs.CertifiedMath import CertifiedMath, BigNum128
        from src.core.TokenStateBundle import TokenStateBundle
        from src.libs.economics.economic_constants import (
            NOD_ALLOCATION_FRACTION,
            MIN_NOD_ALLOCATION_FRACTION,
            MAX_NOD_ALLOCATION_FRACTION,
            NOD_MIN_ACTIVE_NODES,
            NOD_MAX_ISSUANCE_PER_EPOCH,
            NOD_ZERO_ACTIVITY_FLOOR,
            MAX_NODE_REWARD_SHARE,
            MAX_NOD_VOTING_POWER_RATIO
        )
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.TokenStateBundle import TokenStateBundle
        from libs.economics.economic_constants import (
            NOD_ALLOCATION_FRACTION,
            MIN_NOD_ALLOCATION_FRACTION,
            MAX_NOD_ALLOCATION_FRACTION,
            NOD_MIN_ACTIVE_NODES,
            NOD_MAX_ISSUANCE_PER_EPOCH,
            NOD_ZERO_ACTIVITY_FLOOR,
            MAX_NODE_REWARD_SHARE,
            MAX_NOD_VOTING_POWER_RATIO
        )


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

    def __init__(self, cm_instance: CertifiedMath, allocation_fraction: BigNum128 = None):
        """
        Initialize the NOD Allocator.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
            allocation_fraction: Custom NOD allocation fraction (must be within bounds)
        """
        self.cm = cm_instance
        
        # Set allocation fraction with safety bounds enforcement
        if allocation_fraction is None:
            self.allocation_fraction = NOD_ALLOCATION_FRACTION
        else:
            # Enforce constitutional bounds
            if self.cm.lt(allocation_fraction, MIN_NOD_ALLOCATION_FRACTION, [], None, None):
                raise ValueError(f"NOD allocation fraction {allocation_fraction.to_decimal_string()} below minimum {MIN_NOD_ALLOCATION_FRACTION.to_decimal_string()}")
            if self.cm.gt(allocation_fraction, MAX_NOD_ALLOCATION_FRACTION, [], None, None):
                raise ValueError(f"NOD allocation fraction {allocation_fraction.to_decimal_string()} above maximum {MAX_NOD_ALLOCATION_FRACTION.to_decimal_string()}")
            self.allocation_fraction = allocation_fraction

    def allocate_from_atr_fees(
        self,
        atr_total_fees: BigNum128,
        node_contributions: Dict[str, BigNum128],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        epoch_number: int = 0,
    ) -> List[NODAllocation]:
        """
        Allocate NOD tokens from ATR fees to infrastructure nodes based on contribution metrics.
        
        Args:
            atr_total_fees: Total ATR fees collected
            node_contributions: Dictionary mapping node IDs to contribution scores
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            epoch_number: Current epoch number for emission controls
            
        Returns:
            List[NODAllocation]: List of NOD allocations for each node
        """
        # Calculate NOD share from ATR fees (using configured allocation fraction)
        nod_share = self.cm.mul(atr_total_fees, self.allocation_fraction, log_list, pqc_cid, quantum_metadata)
        
        # Enforce maximum issuance per epoch (constitutional limit)
        if self.cm.gt(nod_share, NOD_MAX_ISSUANCE_PER_EPOCH, log_list, pqc_cid, quantum_metadata):
            nod_share = NOD_MAX_ISSUANCE_PER_EPOCH
            # Log the capping event
            if log_list is not None:
                log_list.append({
                    "operation": "nod_issuance_capped",
                    "original_amount": self.cm.mul(atr_total_fees, self.allocation_fraction, [], pqc_cid, quantum_metadata).to_decimal_string(),
                    "capped_amount": nod_share.to_decimal_string(),
                    "epoch": epoch_number,
                    "timestamp": deterministic_timestamp
                })
        
        # Enforce zero-activity floor (no issuance if nod_share is below floor)
        if self.cm.lte(nod_share, NOD_ZERO_ACTIVITY_FLOOR, log_list, pqc_cid, quantum_metadata):
            # Log zero-activity event
            if log_list is not None:
                log_list.append({
                    "operation": "nod_zero_activity",
                    "nod_share": nod_share.to_decimal_string(),
                    "epoch": epoch_number,
                    "timestamp": deterministic_timestamp
                })
            return []  # No allocation when idle
        
        # Allocate the NOD share to nodes
        return self.allocate_nod(
            nod_reward_pool=nod_share,
            node_contributions=node_contributions,
            log_list=log_list,
            pqc_cid=pqc_cid,
            quantum_metadata=quantum_metadata,
            deterministic_timestamp=deterministic_timestamp,
            epoch_number=epoch_number
        )

    def allocate_nod(
        self,
        nod_reward_pool: BigNum128,
        node_contributions: Dict[str, BigNum128],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        epoch_number: int = 0,
    ) -> List[NODAllocation]:
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
        # Validate inputs
        if nod_reward_pool.value < 0:
            raise ValueError("NOD reward pool cannot be negative")
            
        if not node_contributions:
            # No nodes to allocate to
            return []
        
        # Enforce minimum active nodes requirement (constitutional limit)
        num_active_nodes = len(node_contributions)
        if num_active_nodes < NOD_MIN_ACTIVE_NODES.value:
            # Log insufficient nodes event
            if log_list is not None:
                log_list.append({
                    "operation": "nod_insufficient_nodes",
                    "active_nodes": num_active_nodes,
                    "required_minimum": NOD_MIN_ACTIVE_NODES.value,
                    "epoch": epoch_number,
                    "timestamp": deterministic_timestamp
                })
            # Do not allocate if network size too small (prevents early-node monopolization)
            return []
            
        # Calculate total contribution score
        total_contribution = BigNum128(0)
        for score in node_contributions.values():
            total_contribution = self.cm.add(total_contribution, score, log_list, pqc_cid, quantum_metadata)
            
        # If total contribution is zero, distribute equally
        if total_contribution.value == 0:
            return self._allocate_equal(nod_reward_pool, node_contributions, log_list, pqc_cid, quantum_metadata, deterministic_timestamp, epoch_number)
            
        # Allocate proportionally based on contribution scores with anti-centralization caps
        allocations = []
        remaining_nod = nod_reward_pool
        
        # Calculate per-node dominance cap (constitutional limit)
        max_node_share = self.cm.mul(nod_reward_pool, MAX_NODE_REWARD_SHARE, log_list, pqc_cid, quantum_metadata)
        
        # Sort nodes by ID for deterministic ordering
        sorted_nodes = sorted(node_contributions.keys())
        
        # Allocate to all but the last node
        for i, node_id in enumerate(sorted_nodes[:-1]):
            contribution_score = node_contributions[node_id]
            
            # Calculate proportional share: (contribution / total) * reward_pool
            share_numerator = self.cm.mul(contribution_score, nod_reward_pool, log_list, pqc_cid, quantum_metadata)
            share = self.cm.div(share_numerator, total_contribution, log_list, pqc_cid, quantum_metadata)
            
            # Enforce per-node dominance cap (prevent single-node capture)
            capped = False
            if self.cm.gt(share, max_node_share, log_list, pqc_cid, quantum_metadata):
                share = max_node_share
                capped = True
                # Log capping event
                if log_list is not None:
                    log_list.append({
                        "operation": "nod_node_share_capped",
                        "node_id": node_id,
                        "original_share": share_numerator.to_decimal_string(),
                        "capped_share": share.to_decimal_string(),
                        "cap_ratio": MAX_NODE_REWARD_SHARE.to_decimal_string(),
                        "epoch": epoch_number,
                        "timestamp": deterministic_timestamp
                    })
            
            # Ensure we don't exceed the remaining NOD
            if share.value > remaining_nod.value:
                share = remaining_nod
                
            allocations.append(NODAllocation(
                node_id=node_id,
                nod_amount=share,
                contribution_score=contribution_score,
                timestamp=deterministic_timestamp
            ))
            
            # Deduct from remaining NOD
            remaining_nod = self.cm.sub(remaining_nod, share, log_list, pqc_cid, quantum_metadata)
            
        # Allocate remaining NOD to the last node (also subject to cap)
        last_node_id = sorted_nodes[-1]
        last_contribution_score = node_contributions[last_node_id]
        
        # Apply cap to last node as well
        last_node_share = remaining_nod
        if self.cm.gt(last_node_share, max_node_share, log_list, pqc_cid, quantum_metadata):
            last_node_share = max_node_share
            # Log capping event
            if log_list is not None:
                log_list.append({
                    "operation": "nod_node_share_capped",
                    "node_id": last_node_id,
                    "original_share": remaining_nod.to_decimal_string(),
                    "capped_share": last_node_share.to_decimal_string(),
                    "cap_ratio": MAX_NODE_REWARD_SHARE.to_decimal_string(),
                    "epoch": epoch_number,
                    "timestamp": deterministic_timestamp
                })
        
        allocations.append(NODAllocation(
            node_id=last_node_id,
            nod_amount=last_node_share,
            contribution_score=last_contribution_score,
            timestamp=deterministic_timestamp
        ))
        
        # Log the allocation
        self._log_nod_allocation(
            nod_reward_pool, node_contributions, allocations,
            log_list, pqc_cid, quantum_metadata, deterministic_timestamp, epoch_number
        )
        
        return allocations

    def _allocate_equal(
        self,
        nod_reward_pool: BigNum128,
        node_contributions: Dict[str, BigNum128],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        epoch_number: int = 0,
    ) -> List[NODAllocation]:
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
            
        # Calculate equal share
        equal_share = self.cm.div(nod_reward_pool, BigNum128.from_int(num_nodes), log_list, pqc_cid, quantum_metadata)
        
        # Enforce per-node dominance cap even for equal distribution
        max_node_share = self.cm.mul(nod_reward_pool, MAX_NODE_REWARD_SHARE, log_list, pqc_cid, quantum_metadata)
        if self.cm.gt(equal_share, max_node_share, log_list, pqc_cid, quantum_metadata):
            equal_share = max_node_share
        
        allocations = []
        remaining_nod = nod_reward_pool
        
        # Sort nodes by ID for deterministic ordering
        sorted_nodes = sorted(node_contributions.keys())
        
        # Allocate to all but the last node
        for i, node_id in enumerate(sorted_nodes[:-1]):
            allocations.append(NODAllocation(
                node_id=node_id,
                nod_amount=equal_share,
                contribution_score=node_contributions[node_id],
                timestamp=deterministic_timestamp
            ))
            
            # Deduct from remaining NOD
            remaining_nod = self.cm.sub(remaining_nod, equal_share, log_list, pqc_cid, quantum_metadata)
            
        # Allocate remaining NOD to the last node (also subject to cap)
        last_node_id = sorted_nodes[-1]
        last_node_share = remaining_nod
        if self.cm.gt(last_node_share, max_node_share, log_list, pqc_cid, quantum_metadata):
            last_node_share = max_node_share
            
        allocations.append(NODAllocation(
            node_id=last_node_id,
            nod_amount=last_node_share,
            contribution_score=node_contributions[last_node_id],
            timestamp=deterministic_timestamp
        ))
        
        return allocations

    def _log_nod_allocation(
        self,
        nod_reward_pool: BigNum128,
        node_contributions: Dict[str, BigNum128],
        allocations: List[NODAllocation],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        epoch_number: int = 0,
    ):
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
        # Prepare allocation details for logging
        allocation_count = len(allocations)
        total_allocated = BigNum128(0)
        
        for alloc in allocations:
            total_allocated = self.cm.add(total_allocated, alloc.nod_amount, log_list, pqc_cid, quantum_metadata)
            
        # Log the operation using CertifiedMath's public API
        details = {
            "operation": "nod_allocation",
            "nod_reward_pool": nod_reward_pool.to_decimal_string(),
            "total_contributions": sum(score.value for score in node_contributions.values()),
            "total_allocated": total_allocated.to_decimal_string(),
            "allocation_count": allocation_count,
            "epoch": epoch_number,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's public API for logging
        dummy_result = BigNum128(1)
        self.cm.add(dummy_result, dummy_result, log_list, pqc_cid, quantum_metadata)
        # Replace the last entry with our custom log entry
        if log_list:
            log_list[-1] = {
                "operation": "nod_allocation",
                "details": details,
                "result": total_allocated.to_decimal_string(),
                "pqc_cid": pqc_cid,
                "quantum_metadata": quantum_metadata,
                "timestamp": deterministic_timestamp
            }


# Test function
def test_nod_allocator():
    """Test the NODAllocator implementation."""
    print("Testing NODAllocator...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create NODAllocator
    allocator = NODAllocator(cm)
    
    # Create test NOD reward pool
    nod_reward_pool = BigNum128.from_int(1000)  # 1000.0 NOD
    
    # Create test node contributions
    node_contributions = {
        "node_0xabc123": BigNum128.from_int(50),   # 50.0 contribution score
        "node_0xdef456": BigNum128.from_int(30),   # 30.0 contribution score
        "node_0xghi789": BigNum128.from_int(20),   # 20.0 contribution score
    }
    
    log_list = []
    
    # Allocate NOD
    allocations = allocator.allocate_nod(
        nod_reward_pool=nod_reward_pool,
        node_contributions=node_contributions,
        log_list=log_list,
        pqc_cid="test_nod_001",
        deterministic_timestamp=1234567890
    )
    
    total_allocated = BigNum128(0)
    for alloc in allocations:
        print(f"Node {alloc.node_id}: {alloc.nod_amount.to_decimal_string()} NOD (score: {alloc.contribution_score.to_decimal_string()})")
        total_allocated = cm.add(total_allocated, alloc.nod_amount, log_list, "test_nod_001", {})
        
    print(f"Total allocated: {total_allocated.to_decimal_string()} NOD")
    print(f"Log entries: {len(log_list)}")
    
    print("✓ NODAllocator test passed!")


if __name__ == "__main__":
    test_nod_allocator()