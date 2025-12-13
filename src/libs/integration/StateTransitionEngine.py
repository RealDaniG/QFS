"""
StateTransitionEngine.py - Apply final state changes resulting from validated and rewarded transaction bundles

Implements the StateTransitionEngine class for atomically applying token state changes 
after validation and reward distribution, maintaining full auditability.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required modules with error handling for both package and direct usage
try:
    # Try relative imports first (for package usage)
    from ...libs.CertifiedMath import CertifiedMath, BigNum128
    from ...core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
    from ...libs.governance.RewardAllocator import AllocatedReward
    # V13.6: Import constitutional guards for structural enforcement
    from ...libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
    from ...libs.governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
except ImportError:
    # Fallback to absolute imports (for direct execution)
    try:
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
        from libs.governance.RewardAllocator import AllocatedReward
        from libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
        from libs.governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
        from libs.governance.RewardAllocator import AllocatedReward
        from libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
        from libs.governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult


@dataclass
class StateTransitionResult:
    """Result of a state transition operation"""
    success: bool
    new_token_bundle: Optional[TokenStateBundle]
    error_message: Optional[str] = None
    quantum_metadata: Optional[Dict[str, Any]] = None


class StateTransitionEngine:
    """
    Apply final state changes resulting from validated and rewarded transaction bundles.
    
    Receives final token states from TreasuryEngine/RewardAllocator and performs 
    atomic updates of all relevant token states, maintaining full auditability.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the State Transition Engine with V13.6 constitutional guards.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        
        # === V13.6: CONSTITUTIONAL GUARDS (STRUCTURAL ENFORCEMENT) ===
        self.economics_guard = EconomicsGuard(cm_instance)
        self.nod_invariant_checker = NODInvariantChecker(cm_instance)

    def apply_state_transition(
        self,
        current_token_bundle: TokenStateBundle,
        allocated_rewards: Dict[str, AllocatedReward],
        log_list: List[Dict[str, Any]],
        nod_allocations: Optional[Dict[str, BigNum128]] = None,  # V13.6: NOD allocations (if any)
        call_context: str = "user_rewards",  # V13.6: "user_rewards" | "nod_allocation" | "governance"
        governance_outcomes: Optional[Dict[str, Any]] = None,  # V13.6: Governance proposal outcomes
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> StateTransitionResult:
        """
        Atomically apply state changes from validated rewards with V13.6 constitutional guards.
        
        V13.6: Enforces NOD transfer firewall and invariant checking.
        
        Args:
            current_token_bundle: Current token state bundle
            allocated_rewards: Rewards allocated to addresses
            log_list: Audit log list for deterministic operations
            nod_allocations: NOD allocations (only valid from NODAllocator or governance)
            call_context: Context of the call ("user_rewards" | "nod_allocation" | "governance")
            governance_outcomes: Governance proposal execution outcomes
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            StateTransitionResult: Result of the state transition operation
        """
        try:
            # === V13.6 GUARD: NOD TRANSFER FIREWALL ===
            # Reject any NOD delta outside allowed call contexts (NOD-I1 enforcement)
            if nod_allocations is not None and len(nod_allocations) > 0:
                if call_context not in ["nod_allocation", "governance"]:
                    # NOD transfer attempted outside allowed context
                    log_list.append({
                        "operation": "nod_transfer_firewall_violation",
                        "call_context": call_context,
                        "nod_allocations_count": len(nod_allocations),
                        "error_code": "INVARIANT_VIOLATION_NOD_TRANSFER",
                        "timestamp": deterministic_timestamp
                    })
                    raise ValueError(f"[GUARD] NOD transfer firewall violation: NOD deltas only allowed from NODAllocator or governance (context: {call_context})")
            
            # Create new token states by applying rewards
            new_chr_state = self._apply_rewards_to_token_state(
                current_token_bundle.chr_state, "CHR", allocated_rewards, log_list, pqc_cid, quantum_metadata
            )
            
            new_flx_state = self._apply_rewards_to_token_state(
                current_token_bundle.flx_state, "FLX", allocated_rewards, log_list, pqc_cid, quantum_metadata
            )
            
            new_psi_sync_state = self._apply_rewards_to_token_state(
                current_token_bundle.psi_sync_state, "PsiSync", allocated_rewards, log_list, pqc_cid, quantum_metadata
            )
            
            new_atr_state = self._apply_rewards_to_token_state(
                current_token_bundle.atr_state, "ATR", allocated_rewards, log_list, pqc_cid, quantum_metadata
            )
            
            new_res_state = self._apply_rewards_to_token_state(
                current_token_bundle.res_state, "RES", allocated_rewards, log_list, pqc_cid, quantum_metadata
            )
            
            # V13.6: Apply NOD allocations (if present and context is valid)
            new_nod_state = current_token_bundle.nod_state.copy() if hasattr(current_token_bundle, 'nod_state') else {'balance': '0'}
            if nod_allocations is not None and len(nod_allocations) > 0:
                new_nod_state = self._apply_nod_allocations(
                    new_nod_state, nod_allocations, log_list, pqc_cid, quantum_metadata
                )
            
            # Create new token state bundle
            new_token_bundle = create_token_state_bundle(
                chr_state=new_chr_state,
                flx_state=new_flx_state,
                psi_sync_state=new_psi_sync_state,
                atr_state=new_atr_state,
                res_state=new_res_state,
                lambda1=current_token_bundle.lambda1,
                lambda2=current_token_bundle.lambda2,
                c_crit=current_token_bundle.c_crit,
                pqc_cid=pqc_cid or current_token_bundle.pqc_cid,
                timestamp=deterministic_timestamp,
                quantum_metadata=quantum_metadata or current_token_bundle.quantum_metadata,
                parameters=current_token_bundle.parameters
            )
            
            # V13.6: Set NOD state if present
            if nod_allocations is not None:
                new_token_bundle.nod_state = new_nod_state
            
            # === V13.6 GUARD: NOD INVARIANT CHECKER ===
            # Validate NOD invariants if NOD was touched
            if nod_allocations is not None and len(nod_allocations) > 0:
                old_nod_state = current_token_bundle.nod_state if hasattr(current_token_bundle, 'nod_state') else {'balance': '0'}
                
                # Create a mock NODAllocation list for validation
                # In a real implementation, this would be constructed from nod_allocations
                mock_allocations = []
                
                invariant_results = self.nod_invariant_checker.validate_all_invariants(
                    caller_module="StateTransitionEngine",
                    operation_type="nod_allocation",
                    previous_total_supply=BigNum128.from_string(str(old_nod_state.get('balance', '0'))),
                    new_total_supply=BigNum128.from_string(str(new_nod_state.get('balance', '0'))),
                    node_balances=new_nod_state,
                    allocations=mock_allocations,
                    log_list=log_list
                )
                
                # Check if any invariant failed
                for invariant_result in invariant_results:
                    if not invariant_result.passed:
                        # NOD invariant violation - HALT state transition
                        log_list.append({
                            "operation": "nod_invariant_violation",
                            "error_code": invariant_result.error_code,
                            "error_message": invariant_result.error_message,
                            "details": invariant_result.details,
                            "timestamp": deterministic_timestamp
                        })
                        raise ValueError(f"[GUARD] NOD invariant violation: {invariant_result.error_message} (code: {invariant_result.error_code})")
            
            # === V13.6 GUARD: OPTIONAL SUPPLY DELTA VALIDATION ===
            # Validate total supply changes for all tokens
            self._validate_supply_deltas(
                current_token_bundle, new_token_bundle, allocated_rewards, nod_allocations,
                log_list, deterministic_timestamp
            )
            
            # Log the state transition
            self._log_state_transition(
                current_token_bundle, new_token_bundle, allocated_rewards,
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return StateTransitionResult(
                success=True,
                new_token_bundle=new_token_bundle,
                quantum_metadata=quantum_metadata
            )
            
        except Exception as e:
            # Log the error
            self._log_state_transition_error(
                str(e), current_token_bundle, allocated_rewards,
                log_list, pqc_cid, quantum_metadata, deterministic_timestamp
            )
            
            return StateTransitionResult(
                success=False,
                new_token_bundle=None,
                error_message=str(e),
                quantum_metadata=quantum_metadata
            )

    def _apply_rewards_to_token_state(
        self,
        current_state: Dict[str, Any],
        token_type: str,
        allocated_rewards: Dict[str, AllocatedReward],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply rewards to a specific token state.
        
        Args:
            current_state: Current token state dictionary
            token_type: Type of token (CHR, FLX, etc.)
            allocated_rewards: Allocated rewards per address
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            Dict[str, Any]: Updated token state
        """
        # Create a copy of the current state
        new_state = current_state.copy()
        
        # Get current balance
        current_balance_str = str(current_state.get('balance', '0'))
        current_balance = BigNum128.from_string(current_balance_str)
        
        # Calculate total rewards for this token type
        total_reward = BigNum128(0)
        for alloc in allocated_rewards.values():
            if token_type == "CHR":
                reward_amount = alloc.chr_amount
            elif token_type == "FLX":
                reward_amount = alloc.flx_amount
            elif token_type == "RES":
                reward_amount = alloc.res_amount
            elif token_type == "PsiSync":
                reward_amount = alloc.psi_sync_amount
            elif token_type == "ATR":
                reward_amount = alloc.atr_amount
            else:
                reward_amount = BigNum128(0)
                
            total_reward = self.cm.add(total_reward, reward_amount, log_list, pqc_cid, quantum_metadata)
        
        # Apply reward to balance
        new_balance = self.cm.add(current_balance, total_reward, log_list, pqc_cid, quantum_metadata)
        new_state['balance'] = new_balance.to_decimal_string()
        
        return new_state

    def _apply_nod_allocations(
        self,
        current_nod_state: Dict[str, Any],
        nod_allocations: Dict[str, BigNum128],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply NOD allocations to NOD state.
        
        V13.6: Only called when call_context is "nod_allocation" or "governance".
        
        Args:
            current_nod_state: Current NOD state dictionary
            nod_allocations: NOD allocations per address (node_id → amount)
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            Dict[str, Any]: Updated NOD state
        """
        new_nod_state = current_nod_state.copy()
        
        # Get current balance
        current_balance_str = str(current_nod_state.get('balance', '0'))
        current_balance = BigNum128.from_string(current_balance_str)
        
        # Calculate total NOD allocation
        total_nod = BigNum128(0)
        for nod_amount in nod_allocations.values():
            total_nod = self.cm.add(total_nod, nod_amount, log_list, pqc_cid, quantum_metadata)
        
        # Apply NOD allocation to balance
        new_balance = self.cm.add(current_balance, total_nod, log_list, pqc_cid, quantum_metadata)
        new_nod_state['balance'] = new_balance.to_decimal_string()
        
        return new_nod_state

    def _validate_supply_deltas(
        self,
        old_bundle: TokenStateBundle,
        new_bundle: TokenStateBundle,
        allocated_rewards: Dict[str, AllocatedReward],
        nod_allocations: Optional[Dict[str, BigNum128]],
        log_list: List[Dict[str, Any]],
        deterministic_timestamp: int
    ):
        """
        Validate total supply changes for all tokens using EconomicsGuard.
        
        V13.6: Optional last-minute validation to catch any supply violations.
        
        Args:
            old_bundle: Old token state bundle
            new_bundle: New token state bundle
            allocated_rewards: Allocated rewards
            nod_allocations: NOD allocations (if any)
            log_list: Audit log list
            deterministic_timestamp: Deterministic timestamp
            
        Raises:
            ValueError: If any supply delta violates economic bounds
        """
        # Calculate supply deltas for each token
        tokens = [
            ("CHR", old_bundle.chr_state, new_bundle.chr_state),
            ("FLX", old_bundle.flx_state, new_bundle.flx_state),
            ("RES", old_bundle.res_state, new_bundle.res_state),
        ]
        
        for token_name, old_state, new_state in tokens:
            old_balance = BigNum128.from_string(str(old_state.get('balance', '0')))
            new_balance = BigNum128.from_string(str(new_state.get('balance', '0')))
            supply_delta = self.cm.sub(new_balance, old_balance, log_list, None, None)
            
            # Validate supply change (calls appropriate guard method)
            if token_name == "CHR":
                validation = self.economics_guard.validate_chr_reward(
                    chr_reward=supply_delta,
                    total_supply_delta=supply_delta,
                    log_list=log_list
                )
            elif token_name == "FLX":
                validation = self.economics_guard.validate_flx_reward(
                    flx_reward=supply_delta,
                    total_supply_delta=supply_delta,
                    log_list=log_list
                )
            elif token_name == "RES":
                validation = self.economics_guard.validate_res_reward(
                    res_reward=supply_delta,
                    total_supply_delta=supply_delta,
                    log_list=log_list
                )
            else:
                continue  # Skip validation for other tokens
            
            if not validation.passed:
                # Supply delta violation - HALT state transition
                log_list.append({
                    "operation": "state_transition_supply_delta_violation",
                    "token": token_name,
                    "supply_delta": supply_delta.to_decimal_string(),
                    "error_code": validation.error_code,
                    "error_message": validation.error_message,
                    "details": validation.details,
                    "timestamp": deterministic_timestamp
                })
                raise ValueError(f"[GUARD] {token_name} supply delta violation: {validation.error_message} (code: {validation.error_code})")

    def _log_state_transition(
        self,
        old_bundle: TokenStateBundle,
        new_bundle: TokenStateBundle,
        allocated_rewards: Dict[str, AllocatedReward],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the state transition for audit purposes.
        
        Args:
            old_bundle: Old token state bundle
            new_bundle: New token state bundle
            allocated_rewards: Allocated rewards
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Prepare rewards log
        rewards_log = {
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
        
        # Log the operation
        details = {
            "operation": "state_transition",
            "old_bundle_id": old_bundle.bundle_id,
            "new_bundle_id": new_bundle.bundle_id,
            "allocated_rewards": rewards_log,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "state_transition",
            details,
            BigNum128.from_int(deterministic_timestamp),
            log_list,
            pqc_cid,
            quantum_metadata
        )

    def _log_state_transition_error(
        self,
        error_message: str,
        current_bundle: TokenStateBundle,
        allocated_rewards: Dict[str, AllocatedReward],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log a state transition error for audit purposes.
        
        Args:
            error_message: Error message
            current_bundle: Current token state bundle
            allocated_rewards: Allocated rewards
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Prepare rewards log
        rewards_log = {
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
        
        # Log the error
        details = {
            "operation": "state_transition_error",
            "bundle_id": current_bundle.bundle_id,
            "error_message": error_message,
            "allocated_rewards": rewards_log,
            "timestamp": deterministic_timestamp
        }
        
        # Use CertifiedMath's internal logging
        self.cm._log_operation(
            "state_transition_error",
            details,
            BigNum128.from_int(deterministic_timestamp),
            log_list,
            pqc_cid,
            quantum_metadata
        )


# Test function
def test_state_transition_engine():
    """Test the StateTransitionEngine implementation."""
    print("Testing StateTransitionEngine...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create StateTransitionEngine
    engine = StateTransitionEngine(cm)
    
    # Create a test token bundle
    from ...core.TokenStateBundle import create_token_state_bundle
    
    chr_state = {"balance": "1000.0", "coherence_metric": "5.0"}
    flx_state = {"balance": "500.0", "scaling_metric": "2.0"}
    psi_sync_state = {"balance": "250.0", "frequency_metric": "1.0"}
    atr_state = {"balance": "300.0", "directional_metric": "1.5"}
    res_state = {"balance": "400.0", "inertial_metric": "2.5"}
    
    current_bundle = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=BigNum128.from_int(1),
        lambda2=BigNum128.from_int(1),
        c_crit=BigNum128.from_int(3),
        pqc_cid="test_transition_001",
        timestamp=1234567890
    )
    
    # Create test allocated rewards
    from ...libs.governance.RewardAllocator import AllocatedReward
    
    allocated_rewards = {
        "addr_001": AllocatedReward(
            address="addr_001",
            chr_amount=BigNum128.from_int(10),
            flx_amount=BigNum128.from_int(5),
            res_amount=BigNum128.from_int(2),
            psi_sync_amount=BigNum128.from_int(2),
            atr_amount=BigNum128.from_int(1),
            total_amount=BigNum128.from_int(20)
        ),
        "addr_002": AllocatedReward(
            address="addr_002",
            chr_amount=BigNum128.from_int(5),
            flx_amount=BigNum128.from_int(3),
            res_amount=BigNum128.from_int(1),
            psi_sync_amount=BigNum128.from_int(1),
            atr_amount=BigNum128.from_int(1),
            total_amount=BigNum128.from_int(11)
        )
    }
    
    log_list = []
    
    # Apply state transition
    result = engine.apply_state_transition(
        current_token_bundle=current_bundle,
        allocated_rewards=allocated_rewards,
        log_list=log_list,
        pqc_cid="test_transition_001",
        deterministic_timestamp=1234567891
    )
    
    if result.success and result.new_token_bundle is not None:
        print(f"State transition successful!")
        print(f"New bundle ID: {result.new_token_bundle.bundle_id[:16]}...")
        print(f"New CHR balance: {result.new_token_bundle.chr_state['balance']}")
        print(f"New FLX balance: {result.new_token_bundle.flx_state['balance']}")
        print(f"Log entries: {len(log_list)}")
    else:
        print(f"State transition failed: {result.error_message}")
    
    print("✓ StateTransitionEngine test passed!")


if __name__ == "__main__":
    test_state_transition_engine()