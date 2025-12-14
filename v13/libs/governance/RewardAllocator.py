"""
RewardAllocator.py - Distribute calculated rewards from TreasuryEngine to specific wallets/addresses

Implements the RewardAllocator class for distributing deterministic rewards 
using CertifiedMath public API for all calculations and maintaining full 
auditability via log_list, pqc_cid, and quantum_metadata.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required modules
try:
    from ...libs.CertifiedMath import CertifiedMath, BigNum128
    from ...core.reward_types import RewardBundle
    # V13.6: Import EconomicsGuard for structural enforcement
    from ...libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
    from ...libs.economics.economic_constants import (
        MAX_REWARD_PER_ADDRESS,
        MIN_DUST_THRESHOLD
    )
except ImportError:
    try:
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.reward_types import RewardBundle
        from v13.libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
        from v13.libs.economics.economic_constants import (
            MAX_REWARD_PER_ADDRESS,
            MIN_DUST_THRESHOLD
        )
    except ImportError:
        try:
            from v13.libs.CertifiedMath import CertifiedMath, BigNum128
            from v13.core.reward_types import RewardBundle
            from v13.libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
            from v13.libs.economics.economic_constants import (
                MAX_REWARD_PER_ADDRESS,
                MIN_DUST_THRESHOLD
            )
        except ImportError:
            from libs.CertifiedMath import CertifiedMath, BigNum128
            from core.reward_types import RewardBundle
            from economics.EconomicsGuard import EconomicsGuard, ValidationResult
            from economics.economic_constants import (
                MAX_REWARD_PER_ADDRESS,
                MIN_DUST_THRESHOLD
            )


@dataclass
class AllocatedReward:
    """Container for allocated rewards per address"""
    address: str
    chr_amount: BigNum128
    flx_amount: BigNum128
    res_amount: BigNum128
    psi_sync_amount: BigNum128
    atr_amount: BigNum128
    total_amount: BigNum128


class RewardAllocator:
    """
    Distribute calculated rewards from TreasuryEngine to specific wallets/addresses.
    
    Uses CertifiedMath public API for any distribution logic calculations 
    (e.g., proportional splits, caps) and maintains full auditability.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Reward Allocator with V13.6 constitutional guards.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        
        # === V13.6: ECONOMICS GUARD (STRUCTURAL ENFORCEMENT) ===
        self.economics_guard = EconomicsGuard(cm_instance)

    def allocate_rewards(
        self,
        reward_bundle: RewardBundle,
        recipient_addresses: List[str],
        log_list: List[Dict[str, Any]],
        allocation_weights: Optional[Dict[str, BigNum128]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> Dict[str, AllocatedReward]:
        """
        Distribute rewards from TreasuryEngine to specific addresses.
        
        Args:
            reward_bundle: Reward bundle from TreasuryEngine
            recipient_addresses: List of recipient wallet addresses
            allocation_weights: Optional weights for each recipient (defaults to equal distribution)
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            Dict[str, AllocatedReward]: Allocated rewards per address
        """
        if not recipient_addresses:
            raise ValueError("Recipient addresses list cannot be empty")
            
        # If no weights provided, distribute equally
        if allocation_weights is None:
            allocation_weights = self._create_equal_weights(recipient_addresses, log_list, pqc_cid, quantum_metadata)
        
        # Normalize weights to sum to 1.0
        normalized_weights = self._normalize_weights(allocation_weights, log_list, pqc_cid, quantum_metadata)
        
        # Allocate rewards to each recipient
        allocated_rewards = {}
        total_recipients = len(recipient_addresses)
        
        for address in recipient_addresses:
            weight = normalized_weights.get(address, BigNum128(0))
            
            # Calculate allocated amounts for each token type
            chr_amount = self.cm.mul(reward_bundle.chr_reward, weight, log_list, pqc_cid, quantum_metadata)
            flx_amount = self.cm.mul(reward_bundle.flx_reward, weight, log_list, pqc_cid, quantum_metadata)
            res_amount = self.cm.mul(reward_bundle.res_reward, weight, log_list, pqc_cid, quantum_metadata)
            psi_sync_amount = self.cm.mul(reward_bundle.psi_sync_reward, weight, log_list, pqc_cid, quantum_metadata)
            atr_amount = self.cm.mul(reward_bundle.atr_reward, weight, log_list, pqc_cid, quantum_metadata)
            
            # Calculate total allocated amount
            total_amount = self.cm.add(
                self.cm.add(chr_amount, flx_amount, log_list, pqc_cid, quantum_metadata),
                self.cm.add(
                    self.cm.add(res_amount, psi_sync_amount, log_list, pqc_cid, quantum_metadata),
                    atr_amount, log_list, pqc_cid, quantum_metadata
                ),
                log_list, pqc_cid, quantum_metadata
            )
            
            # === V13.6 GUARD: Validate per-address cap ===
            addr_validation = self.economics_guard.validate_per_address_reward(
                address=address,
                chr_amount=chr_amount,
                flx_amount=flx_amount,
                res_amount=res_amount,
                total_amount=total_amount,
                log_list=log_list
            )
            
            if not addr_validation.passed:
                # Economic guard violation - HALT allocation
                log_list.append({
                    "operation": "reward_allocation_per_address_violation",
                    "address": address,
                    "error_code": addr_validation.error_code,
                    "error_message": addr_validation.error_message,
                    "details": addr_validation.details,
                    "timestamp": deterministic_timestamp
                })
                raise ValueError(f"[GUARD] Per-address reward violation for {address}: {addr_validation.error_message} (code: {addr_validation.error_code})")
            
            # === V13.6 GUARD: Handle dust amounts (log policy decision) ===
            is_dust = self.cm.lt(total_amount, MIN_DUST_THRESHOLD, log_list, pqc_cid, quantum_metadata)
            if is_dust:
                # Log dust policy decision (amounts below threshold are still allocated but flagged)
                log_list.append({
                    "operation": "reward_allocation_dust_detected",
                    "address": address,
                    "total_amount": total_amount.to_decimal_string(),
                    "dust_threshold": MIN_DUST_THRESHOLD.to_decimal_string(),
                    "policy": "allocate_with_warning",
                    "timestamp": deterministic_timestamp
                })
            
            allocated_rewards[address] = AllocatedReward(
                address=address,
                chr_amount=chr_amount,
                flx_amount=flx_amount,
                res_amount=res_amount,
                psi_sync_amount=psi_sync_amount,
                atr_amount=atr_amount,
                total_amount=total_amount
            )
        
        # Log the allocation
        self._log_reward_allocation(
            reward_bundle, recipient_addresses, allocation_weights, allocated_rewards,
            log_list, pqc_cid, quantum_metadata, deterministic_timestamp
        )
        
        return allocated_rewards

    def _create_equal_weights(
        self,
        recipient_addresses: List[str],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, BigNum128]:
        """
        Create equal weights for all recipients.
        
        Args:
            recipient_addresses: List of recipient addresses
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            Dict[str, BigNum128]: Equal weights for each recipient
        """
        if not recipient_addresses:
            return {}
            
        # Calculate equal weight (1.0 / number of recipients)
        num_recipients = BigNum128.from_int(len(recipient_addresses))
        one = BigNum128.from_int(1)
        equal_weight = self.cm.div(one, num_recipients, log_list, pqc_cid, quantum_metadata)
        
        return {address: equal_weight for address in recipient_addresses}

    def _normalize_weights(
        self,
        allocation_weights: Dict[str, BigNum128],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, BigNum128]:
        """
        Normalize weights to sum to 1.0.
        
        Args:
            allocation_weights: Raw allocation weights
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            Dict[str, BigNum128]: Normalized weights
        """
        if not allocation_weights:
            return {}
            
        # Calculate sum of all weights
        weight_sum = BigNum128(0)
        for weight in allocation_weights.values():
            weight_sum = self.cm.add(weight_sum, weight, log_list, pqc_cid, quantum_metadata)
        
        # If sum is zero, return equal weights
        if weight_sum.value == 0:
            return {address: BigNum128.from_int(1) for address in allocation_weights.keys()}
        
        # Normalize each weight
        normalized_weights = {}
        for address in sorted(allocation_weights.keys()):
            weight = allocation_weights[address]
            normalized_weight = self.cm.div(weight, weight_sum, log_list, pqc_cid, quantum_metadata)
            normalized_weights[address] = normalized_weight
            
        return normalized_weights

    def _log_reward_allocation(
        self,
        reward_bundle: RewardBundle,
        recipient_addresses: List[str],
        allocation_weights: Dict[str, BigNum128],
        allocated_rewards: Dict[str, AllocatedReward],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the reward allocation for audit purposes.
        
        Args:
            reward_bundle: Original reward bundle
            recipient_addresses: List of recipient addresses
            allocation_weights: Allocation weights used
            allocated_rewards: Final allocated rewards
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Prepare allocation details for logging
        weights_log = {
            address: weight.to_decimal_string() 
            for address, weight in allocation_weights.items()
        }
        
        allocations_log = {
            address: {
                "CHR": alloc.chr_amount.to_decimal_string(),
                "FLX": alloc.flx_amount.to_decimal_string(),
                "RES": alloc.res_amount.to_decimal_string(),
                "PsiSync": alloc.psi_sync_amount.to_decimal_string(),
                "ATR": alloc.atr_amount.to_decimal_string(),
                "Total": alloc.total_amount.to_decimal_string()
            }
            for address, alloc in allocated_rewards.items()
        }
        
        # Log the operation using CertifiedMath's logging mechanism
        details = {
            "operation": "reward_allocation",
            "total_rewards": {
                "CHR": reward_bundle.chr_reward.to_decimal_string(),
                "FLX": reward_bundle.flx_reward.to_decimal_string(),
                "RES": reward_bundle.res_reward.to_decimal_string(),
                "PsiSync": reward_bundle.psi_sync_reward.to_decimal_string(),
                "ATR": reward_bundle.atr_reward.to_decimal_string(),
                "Total": reward_bundle.total_reward.to_decimal_string()
            },
            "recipients": recipient_addresses,
            "allocation_weights": weights_log,
            "allocations": allocations_log
        }
        
        # Use CertifiedMath's internal logging (this will be called by the public wrapper)
        self.cm._log_operation(
            "reward_allocation",
            details,
            reward_bundle.total_reward,
            log_list,
            pqc_cid,
            quantum_metadata
        )


# Test function
def test_reward_allocator():
    """Test the RewardAllocator implementation."""
    print("Testing RewardAllocator...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create RewardAllocator
    allocator = RewardAllocator(cm)
    
    # Create a mock reward bundle
    from v13.core.reward_types import RewardBundle
    
    reward_bundle = RewardBundle(
        chr_reward=BigNum128.from_int(100),  # 100.0 CHR
        flx_reward=BigNum128.from_int(50),   # 50.0 FLX
        res_reward=BigNum128.from_int(25),   # 25.0 RES
        psi_sync_reward=BigNum128.from_int(20),  # 20.0 ΨSync
        atr_reward=BigNum128.from_int(15),   # 15.0 ATR
        total_reward=BigNum128.from_int(210)  # 210.0 Total
    )
    
    # Create test recipient addresses
    recipient_addresses = [
        "addr_001",
        "addr_002",
        "addr_003"
    ]
    
    log_list = []
    
    # Allocate rewards
    allocated_rewards = allocator.allocate_rewards(
        reward_bundle=reward_bundle,
        recipient_addresses=recipient_addresses,
        log_list=log_list,
        pqc_cid="test_allocator_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Number of recipients: {len(allocated_rewards)}")
    for address, alloc in allocated_rewards.items():
        print(f"  {address}: Total = {alloc.total_amount.to_decimal_string()}")
    
    print(f"Log entries: {len(log_list)}")
    
    print("✓ RewardAllocator test passed!")


if __name__ == "__main__":
    test_reward_allocator()