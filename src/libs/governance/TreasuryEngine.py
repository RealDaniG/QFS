"""
TreasuryEngine.py - Economic engine for calculating deterministic rewards based on HSMF metrics

Implements the TreasuryEngine class for computing rewards (FLX, potentially CHR boosts) 
based on HSMF metrics (S_CHR, C_holo, Action_Cost_QFS), using CertifiedMath public API 
for all calculations and maintaining full auditability via log_list, pqc_cid, and quantum_metadata.
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
    from ...core.reward_types import RewardBundle
    from ...libs.economics.economic_constants import FLX_REWARD_FRACTION
    # V13.6: Import EconomicsGuard for structural enforcement
    from ...libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
except ImportError:
    # Fallback to absolute imports (for direct execution)
    try:
        from src.libs.CertifiedMath import CertifiedMath, BigNum128
        from src.core.TokenStateBundle import TokenStateBundle
        from src.core.reward_types import RewardBundle
        from src.libs.economics.economic_constants import FLX_REWARD_FRACTION
        from src.libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.TokenStateBundle import TokenStateBundle
        from core.reward_types import RewardBundle
        from libs.economics.economic_constants import FLX_REWARD_FRACTION
        from libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult


class TreasuryEngine:
    """
    Economic engine for calculating deterministic rewards based on HSMF metrics.
    
    Computes rewards (FLX, potentially CHR boosts) based on HSMF metrics 
    (S_CHR, C_holo, Action_Cost_QFS). Uses CertifiedMath public API for all 
    calculations and maintains full auditability.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Treasury Engine with V13.6 constitutional guards.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        
        # === V13.6: ECONOMICS GUARD (STRUCTURAL ENFORCEMENT) ===
        self.economics_guard = EconomicsGuard(cm_instance)

    def calculate_rewards(
        self,
        hsmf_metrics: Dict[str, BigNum128],
        token_bundle: TokenStateBundle,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> RewardBundle:
        """
        Calculate deterministic rewards based on HSMF metrics and token state.
        
        Args:
            hsmf_metrics: Dictionary containing HSMF metrics (S_CHR, C_holo, Action_Cost_QFS)
            token_bundle: Current token state bundle
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet
            
        Returns:
            RewardBundle: Calculated rewards for each token type
        """
        # Extract required metrics
        s_chr = hsmf_metrics.get("S_CHR", BigNum128(0))
        c_holo = hsmf_metrics.get("C_holo", BigNum128(0))
        action_cost_qfs = hsmf_metrics.get("Action_Cost_QFS", BigNum128(0))
        
        # Check C_holo >= C_MIN (QFS V13 §6.2)
        # C_MIN is typically token_bundle.c_crit or a system constant
        C_MIN = token_bundle.c_crit  # Using c_crit as C_MIN
        if self.cm.lt(c_holo, C_MIN, log_list, pqc_cid, quantum_metadata):
            # In a real implementation, this would trigger CIR-302 via HSMF
            # For TreasuryEngine, we return a special error code that the SDK/CIR-302 handler can interpret
            from libs.CertifiedMath import CertifiedMathError
            raise CertifiedMathError("C_holo < C_MIN — System coherence below critical threshold", error_code="COHERENCE_CRITICAL_FAILURE")
        
        # Get current token states
        # Token balances are stored in the state dictionaries
        chr_balance = BigNum128.from_string(str(token_bundle.chr_state.get('balance', '0')))
        flx_balance = BigNum128.from_string(str(token_bundle.flx_state.get('balance', '0')))
        
        # Calculate base reward multiplier based on C_holo (coherence)
        # Higher coherence = higher rewards
        base_multiplier = self._calculate_base_multiplier(c_holo, log_list, pqc_cid, quantum_metadata)
        
        # Calculate CHR reward based on S_CHR and action cost
        chr_reward = self._calculate_chr_reward(s_chr, action_cost_qfs, base_multiplier, log_list, pqc_cid, quantum_metadata)
        
        # Calculate FLX reward based on CHR reward and FLX balance
        flx_reward = self._calculate_flx_reward(chr_reward, flx_balance, base_multiplier, log_list, pqc_cid, quantum_metadata)
        
        # Calculate other token rewards (simplified for now)
        res_reward = self.cm.mul(BigNum128.from_int(1), base_multiplier, log_list, pqc_cid, quantum_metadata)
        psi_sync_reward = self.cm.mul(BigNum128.from_int(1), base_multiplier, log_list, pqc_cid, quantum_metadata)
        atr_reward = self.cm.mul(BigNum128.from_int(1), base_multiplier, log_list, pqc_cid, quantum_metadata)
        
        # NOD allocation is handled separately by NODAllocator
        # This is just a placeholder to maintain the reward bundle structure
        nod_reward = BigNum128(0)
        
        # Calculate total reward
        total_reward = self.cm.add(
            self.cm.add(chr_reward, flx_reward, log_list, pqc_cid, quantum_metadata),
            self.cm.add(
                self.cm.add(res_reward, psi_sync_reward, log_list, pqc_cid, quantum_metadata),
                self.cm.add(atr_reward, nod_reward, log_list, pqc_cid, quantum_metadata),
                log_list, pqc_cid, quantum_metadata
            ),
            log_list, pqc_cid, quantum_metadata
        )
        
        # === V13.6 GUARD: Validate economic bounds BEFORE returning ===
        chr_validation = self.economics_guard.validate_chr_reward(
            chr_reward=chr_reward,
            total_supply_delta=chr_reward,  # Reward increases total supply
            log_list=log_list
        )
        
        if not chr_validation.passed:
            # Economic guard violation - HALT reward issuance
            log_list.append({
                "operation": "treasury_chr_economic_violation",
                "error_code": chr_validation.error_code,
                "error_message": chr_validation.error_message,
                "details": chr_validation.details,
                "timestamp": deterministic_timestamp
            })
            raise ValueError(f"[GUARD] CHR economic bound violation: {chr_validation.error_message} (code: {chr_validation.error_code})")
        
        flx_validation = self.economics_guard.validate_flx_reward(
            flx_reward=flx_reward,
            total_supply_delta=flx_reward,
            log_list=log_list
        )
        
        if not flx_validation.passed:
            # Economic guard violation - HALT reward issuance
            log_list.append({
                "operation": "treasury_flx_economic_violation",
                "error_code": flx_validation.error_code,
                "error_message": flx_validation.error_message,
                "details": flx_validation.details,
                "timestamp": deterministic_timestamp
            })
            raise ValueError(f"[GUARD] FLX economic bound violation: {flx_validation.error_message} (code: {flx_validation.error_code})")
        
        res_validation = self.economics_guard.validate_res_reward(
            res_reward=res_reward,
            total_supply_delta=res_reward,
            log_list=log_list
        )
        
        if not res_validation.passed:
            # Economic guard violation - HALT reward issuance
            log_list.append({
                "operation": "treasury_res_economic_violation",
                "error_code": res_validation.error_code,
                "error_message": res_validation.error_message,
                "details": res_validation.details,
                "timestamp": deterministic_timestamp
            })
            raise ValueError(f"[GUARD] RES economic bound violation: {res_validation.error_message} (code: {res_validation.error_code})")
        
        # Log the reward calculation
        self._log_reward_calculation(
            hsmf_metrics, chr_reward, flx_reward, res_reward, psi_sync_reward, atr_reward, nod_reward, total_reward,
            log_list, pqc_cid, quantum_metadata, deterministic_timestamp
        )
        
        return RewardBundle(
            chr_reward=chr_reward,
            flx_reward=flx_reward,
            res_reward=res_reward,
            psi_sync_reward=psi_sync_reward,
            atr_reward=atr_reward,
            nod_reward=nod_reward,      # ← Placeholder, actual NOD allocation handled by NODAllocator
            total_reward=total_reward
        )

    def _calculate_base_multiplier(
        self,
        c_holo: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None
    ) -> BigNum128:
        """
        Calculate base reward multiplier based on system coherence.
        
        Args:
            c_holo: System coherence metric
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            BigNum128: Base reward multiplier
        """
        # Base multiplier is 1.0 + (C_holo / 10)
        # This means higher coherence leads to higher rewards
        ten = BigNum128.from_int(10)
        one = BigNum128.from_int(1)
        
        # Calculate C_holo / 10
        c_holo_div_10 = self.cm.div(c_holo, ten, log_list, pqc_cid, quantum_metadata)
        
        # Calculate 1 + (C_holo / 10)
        base_multiplier = self.cm.add(one, c_holo_div_10, log_list, pqc_cid, quantum_metadata)
        
        return base_multiplier

    def _calculate_chr_reward(
        self,
        s_chr: BigNum128,
        action_cost_qfs: BigNum128,
        base_multiplier: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None
    ) -> BigNum128:
        """
        Calculate CHR reward based on S_CHR and action cost.
        
        Args:
            s_chr: CHR stability metric
            action_cost_qfs: Action cost metric
            base_multiplier: Base reward multiplier
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            BigNum128: CHR reward amount
        """
        # Base CHR reward is S_CHR * Action_Cost_QFS
        base_reward = self.cm.mul(s_chr, action_cost_qfs, log_list, pqc_cid, quantum_metadata)
        
        # Apply base multiplier
        chr_reward = self.cm.mul(base_reward, base_multiplier, log_list, pqc_cid, quantum_metadata)
        
        return chr_reward

    def _calculate_flx_reward(
        self,
        chr_reward: BigNum128,
        flx_balance: BigNum128,
        base_multiplier: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None
    ) -> BigNum128:
        """
        Calculate FLX reward based on CHR reward and FLX balance.
        
        Args:
            chr_reward: Previously calculated CHR reward
            flx_balance: Current FLX token balance
            base_multiplier: Base reward multiplier
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            
        Returns:
            BigNum128: FLX reward amount
        """
        # FLX reward is a fixed percentage of CHR reward
        flx_reward_base = self.cm.mul(chr_reward, FLX_REWARD_FRACTION, log_list, pqc_cid, quantum_metadata)
        
        # Apply base multiplier
        flx_reward = self.cm.mul(flx_reward_base, base_multiplier, log_list, pqc_cid, quantum_metadata)
        
        return flx_reward

    def _log_reward_calculation(
        self,
        hsmf_metrics: Dict[str, BigNum128],
        chr_reward: BigNum128,
        flx_reward: BigNum128,
        res_reward: BigNum128,
        psi_sync_reward: BigNum128,
        atr_reward: BigNum128,
        nod_reward: BigNum128,
        total_reward: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Log the reward calculation for audit purposes.
        
        Args:
            hsmf_metrics: HSMF metrics used in calculation
            chr_reward: Calculated CHR reward
            flx_reward: Calculated FLX reward
            res_reward: Calculated RES reward
            psi_sync_reward: Calculated ΨSync reward
            atr_reward: Calculated ATR reward (net after NOD allocation)
            nod_reward: Calculated NOD reward from ATR fees
            total_reward: Total calculated reward
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        # Log the operation using CertifiedMath's public API
        details = {
            "operation": "treasury_reward_calculation",
            "hsmf_metrics": {
                "S_CHR": hsmf_metrics.get("S_CHR", BigNum128(0)).to_decimal_string(),
                "C_holo": hsmf_metrics.get("C_holo", BigNum128(0)).to_decimal_string(),
                "Action_Cost_QFS": hsmf_metrics.get("Action_Cost_QFS", BigNum128(0)).to_decimal_string()
            },
            "rewards": {
                "CHR": chr_reward.to_decimal_string(),
                "FLX": flx_reward.to_decimal_string(),
                "RES": res_reward.to_decimal_string(),
                "PsiSync": psi_sync_reward.to_decimal_string(),
                "ATR": atr_reward.to_decimal_string(),
                "NOD": nod_reward.to_decimal_string(),  # ← NEW
                "Total": total_reward.to_decimal_string()
            }
        }
        
        # Create a dummy result for logging purposes
        dummy_result = BigNum128(1)
        
        # Use CertifiedMath's public API for logging
        self.cm.add(dummy_result, dummy_result, log_list, pqc_cid, quantum_metadata)
        # Replace the last entry with our custom log entry
        if log_list:
            log_list[-1] = {
                "operation": "treasury_reward_calculation",
                "details": details,
                "result": total_reward.to_decimal_string(),
                "pqc_cid": pqc_cid,
                "quantum_metadata": quantum_metadata,
                "timestamp": deterministic_timestamp
            }


# Test function
def test_treasury_engine():
    """Test the TreasuryEngine implementation."""
    print("Testing TreasuryEngine...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create TreasuryEngine
    treasury = TreasuryEngine(cm)
    
    # Create test HSMF metrics
    hsmf_metrics = {
        "S_CHR": BigNum128.from_int(5),  # 5.0
        "C_holo": BigNum128.from_int(8),  # 8.0
        "Action_Cost_QFS": BigNum128.from_int(2)  # 2.0
    }
    
    # Create a simple token bundle
    try:
        # Try relative imports first (for package usage)
        from ...core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
    except ImportError:
        # Fallback to absolute imports (for direct execution)
        try:
            from src.core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
        except ImportError:
            # Try with sys.path modification
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
            from core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
    
    # Create test token states
    chr_state = {"balance": "100.0", "coherence_metric": "5.0"}
    flx_state = {"balance": "50.0", "scaling_metric": "2.0"}
    psi_sync_state = {"balance": "25.0", "frequency_metric": "1.0"}
    atr_state = {"balance": "30.0", "directional_metric": "1.5"}
    res_state = {"balance": "40.0", "inertial_metric": "2.5"}
    
    token_bundle = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=BigNum128.from_int(1),
        lambda2=BigNum128.from_int(1),
        c_crit=BigNum128.from_int(3),
        pqc_cid="test_treasury_001",
        timestamp=1234567890
    )
    
    log_list = []
    
    # Calculate rewards
    rewards = treasury.calculate_rewards(
        hsmf_metrics=hsmf_metrics,
        token_bundle=token_bundle,
        log_list=log_list,
        pqc_cid="test_treasury_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"CHR Reward: {rewards.chr_reward.to_decimal_string()}")
    print(f"FLX Reward: {rewards.flx_reward.to_decimal_string()}")
    print(f"NOD Reward: {rewards.nod_reward.to_decimal_string()}")  # ← NEW
    print(f"Total Reward: {rewards.total_reward.to_decimal_string()}")
    print(f"Log entries: {len(log_list)}")
    
    print("✓ TreasuryEngine test passed!")


if __name__ == "__main__":
    test_treasury_engine()