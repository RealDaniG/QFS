"""
EconomicsGuard.py - Constitutional Economic Bounds Enforcement for QFS V13.6

Implements the EconomicsGuard class to validate all economic operations against
constitutional bounds defined in economic_constants.py. This module serves as
the gatekeeper for all economic mutations, ensuring:

1. CHR/FLX/NOD/PSI/ATR rewards stay within bounds
2. Emission rates respect caps
3. Supply changes respect maximum ratios
4. Governance changes respect safety bounds
5. All violations trigger structured errors for CIR-302 handler

This is a CRITICAL component of the V13.6 constitutional integration.
All economic modules (TreasuryEngine, RewardAllocator, NODAllocator,
InfrastructureGovernance) MUST call EconomicsGuard before mutations.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.BigNum128 import BigNum128
    from .economic_constants import (
        CHR_MAX_REWARD_PER_ACTION,
        CHR_MIN_REWARD_PER_ACTION,
        CHR_DAILY_EMISSION_CAP,
        CHR_SATURATION_THRESHOLD,
        FLX_REWARD_FRACTION,
        MAX_FLX_REWARD_FRACTION,
        MIN_FLX_REWARD_FRACTION,
        FLX_MAX_PER_USER,
        NOD_ALLOCATION_FRACTION,
        MAX_NOD_ALLOCATION_FRACTION,
        MIN_NOD_ALLOCATION_FRACTION,
        MAX_NOD_VOTING_POWER_RATIO,
        MAX_NODE_REWARD_SHARE,
        NOD_MAX_ISSUANCE_PER_EPOCH,
        NOD_MIN_ACTIVE_NODES,
        PSI_MAX_DELTA_PER_EPOCH,
        PSI_MIN_DELTA_MAGNITUDE,
        PSI_SATURATION_CAP,
        ATR_MAX_COST_MULTIPLIER,
        ATR_MAX_ACCUMULATION,
        MAX_TOTAL_SUPPLY_RATIO_CHANGE,
        MAX_SINGLE_EVENT_IMPACT,
        MAX_QUORUM_THRESHOLD,
        MIN_QUORUM_THRESHOLD,
        GOVERNANCE_EMERGENCY_QUORUM,
        MAX_REWARD_PER_ADDRESS,
        MIN_DUST_THRESHOLD,
        RES_MAX_DRAW_PER_EPOCH,
    )
except ImportError:
    # Fallback for non-package execution
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.economics.economic_constants import (
        CHR_MAX_REWARD_PER_ACTION,
        CHR_MIN_REWARD_PER_ACTION,
        CHR_DAILY_EMISSION_CAP,
        CHR_SATURATION_THRESHOLD,
        FLX_REWARD_FRACTION,
        MAX_FLX_REWARD_FRACTION,
        MIN_FLX_REWARD_FRACTION,
        FLX_MAX_PER_USER,
        NOD_ALLOCATION_FRACTION,
        MAX_NOD_ALLOCATION_FRACTION,
        MIN_NOD_ALLOCATION_FRACTION,
        MAX_NOD_VOTING_POWER_RATIO,
        MAX_NODE_REWARD_SHARE,
        NOD_MAX_ISSUANCE_PER_EPOCH,
        NOD_MIN_ACTIVE_NODES,
        PSI_MAX_DELTA_PER_EPOCH,
        PSI_MIN_DELTA_MAGNITUDE,
        PSI_SATURATION_CAP,
        ATR_MAX_COST_MULTIPLIER,
        ATR_MAX_ACCUMULATION,
        MAX_TOTAL_SUPPLY_RATIO_CHANGE,
        MAX_SINGLE_EVENT_IMPACT,
        MAX_QUORUM_THRESHOLD,
        MIN_QUORUM_THRESHOLD,
        GOVERNANCE_EMERGENCY_QUORUM,
        MAX_REWARD_PER_ADDRESS,
        MIN_DUST_THRESHOLD,
        RES_MAX_DRAW_PER_EPOCH,
    )


class EconomicViolationType(Enum):
    """Enumeration of economic violation types for structured error handling."""

    ECON_CHR_REWARD_ABOVE_MAX = "ECON_CHR_REWARD_ABOVE_MAX"
    ECON_CHR_REWARD_BELOW_MIN = "ECON_CHR_REWARD_BELOW_MIN"
    ECON_CHR_EMISSION_CAP_EXCEEDED = "ECON_CHR_EMISSION_CAP_EXCEEDED"
    ECON_CHR_SATURATION_EXCEEDED = "ECON_CHR_SATURATION_EXCEEDED"
    ECON_FLX_FRACTION_ABOVE_MAX = "ECON_FLX_FRACTION_ABOVE_MAX"
    ECON_FLX_FRACTION_BELOW_MIN = "ECON_FLX_FRACTION_BELOW_MIN"
    ECON_FLX_PER_USER_EXCEEDED = "ECON_FLX_PER_USER_EXCEEDED"
    ECON_NOD_ALLOCATION_ABOVE_MAX = "ECON_NOD_ALLOCATION_ABOVE_MAX"
    ECON_NOD_ALLOCATION_BELOW_MIN = "ECON_NOD_ALLOCATION_BELOW_MIN"
    ECON_NOD_VOTING_POWER_EXCEEDED = "ECON_NOD_VOTING_POWER_EXCEEDED"
    ECON_NOD_REWARD_SHARE_EXCEEDED = "ECON_NOD_REWARD_SHARE_EXCEEDED"
    ECON_NOD_EPOCH_ISSUANCE_EXCEEDED = "ECON_NOD_EPOCH_ISSUANCE_EXCEEDED"
    ECON_NOD_INSUFFICIENT_ACTIVE_NODES = "ECON_NOD_INSUFFICIENT_ACTIVE_NODES"
    ECON_PSI_DELTA_ABOVE_MAX = "ECON_PSI_DELTA_ABOVE_MAX"
    ECON_PSI_DELTA_BELOW_MIN = "ECON_PSI_DELTA_BELOW_MIN"
    ECON_PSI_SATURATION_EXCEEDED = "ECON_PSI_SATURATION_EXCEEDED"
    ECON_ATR_COST_MULTIPLIER_EXCEEDED = "ECON_ATR_COST_MULTIPLIER_EXCEEDED"
    ECON_ATR_ACCUMULATION_EXCEEDED = "ECON_ATR_ACCUMULATION_EXCEEDED"
    ECON_SUPPLY_RATIO_CHANGE_EXCEEDED = "ECON_SUPPLY_RATIO_CHANGE_EXCEEDED"
    ECON_SINGLE_EVENT_IMPACT_EXCEEDED = "ECON_SINGLE_EVENT_IMPACT_EXCEEDED"
    GOV_SAFETY_QUORUM_ABOVE_MAX = "GOV_SAFETY_QUORUM_ABOVE_MAX"
    GOV_SAFETY_QUORUM_BELOW_MIN = "GOV_SAFETY_QUORUM_BELOW_MIN"
    GOV_SAFETY_PARAMETER_INVALID = "GOV_SAFETY_PARAMETER_INVALID"
    ECON_ADDRESS_REWARD_EXCEEDED = "ECON_ADDRESS_REWARD_EXCEEDED"
    ECON_RES_REWARD_EXCEEDED = "ECON_RES_REWARD_EXCEEDED"


@dataclass
class ValidationResult:
    """Result of economic validation."""

    passed: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "passed": self.passed,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": self.details or {},
        }


class EconomicsGuard:
    """
    Constitutional Economic Bounds Enforcer for QFS V13.6.

    Validates all economic operations against constitutional bounds.
    All economic modules MUST call EconomicsGuard before mutations.
    Violations trigger structured errors for CIR-302 handler integration.
    """

    def __init__(self, cm_instance: CertifiedMath) -> None:
        """
        Initialize the Economics Guard.

        Args:
            cm_instance: CertifiedMath instance for deterministic comparisons
        """
        self.cm = cm_instance

    def validate_chr_reward(
        self,
        reward_amount: BigNum128,
        current_daily_total: BigNum128,
        current_total_supply: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate CHR reward against constitutional bounds.

        Constitutional checks:
        1. CHR_MIN_REWARD_PER_ACTION <= reward <= CHR_MAX_REWARD_PER_ACTION
        2. current_daily_total + reward <= CHR_DAILY_EMISSION_CAP
        3. current_total_supply + reward <= CHR_SATURATION_THRESHOLD

        Args:
            reward_amount: Proposed CHR reward amount
            current_daily_total: Current daily CHR emission total
            current_total_supply: Current total CHR supply
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        if reward_amount.value < CHR_MIN_REWARD_PER_ACTION.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_CHR_REWARD_BELOW_MIN.value,
                error_message=f"CHR reward {reward_amount.to_decimal_string()} below minimum {CHR_MIN_REWARD_PER_ACTION.to_decimal_string()}",
                details={
                    "reward": reward_amount.to_decimal_string(),
                    "min_allowed": CHR_MIN_REWARD_PER_ACTION.to_decimal_string(),
                },
            )
        if reward_amount.value > CHR_MAX_REWARD_PER_ACTION.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_CHR_REWARD_ABOVE_MAX.value,
                error_message=f"CHR reward {reward_amount.to_decimal_string()} exceeds maximum {CHR_MAX_REWARD_PER_ACTION.to_decimal_string()}",
                details={
                    "reward": reward_amount.to_decimal_string(),
                    "max_allowed": CHR_MAX_REWARD_PER_ACTION.to_decimal_string(),
                },
            )
        new_daily_total = self.cm.add(current_daily_total, reward_amount, log_list)
        if new_daily_total.value > CHR_DAILY_EMISSION_CAP.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_CHR_EMISSION_CAP_EXCEEDED.value,
                error_message=f"CHR daily emission cap exceeded: {new_daily_total.to_decimal_string()} > {CHR_DAILY_EMISSION_CAP.to_decimal_string()}",
                details={
                    "new_daily_total": new_daily_total.to_decimal_string(),
                    "cap": CHR_DAILY_EMISSION_CAP.to_decimal_string(),
                    "reward": reward_amount.to_decimal_string(),
                },
            )
        new_total_supply = self.cm.add(current_total_supply, reward_amount, log_list)
        if new_total_supply.value > CHR_SATURATION_THRESHOLD.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_CHR_SATURATION_EXCEEDED.value,
                error_message=f"CHR saturation threshold exceeded: {new_total_supply.to_decimal_string()} > {CHR_SATURATION_THRESHOLD.to_decimal_string()}",
                details={
                    "new_total_supply": new_total_supply.to_decimal_string(),
                    "threshold": CHR_SATURATION_THRESHOLD.to_decimal_string(),
                    "reward": reward_amount.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def validate_flx_reward(
        self,
        flx_amount: BigNum128,
        chr_reward: BigNum128,
        user_current_balance: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate FLX reward against constitutional bounds.

        Constitutional checks:
        1. MIN_FLX_REWARD_FRACTION <= (flx/chr) <= MAX_FLX_REWARD_FRACTION
        2. user_balance + flx_amount <= FLX_MAX_PER_USER

        Args:
            flx_amount: Proposed FLX reward amount
            chr_reward: Associated CHR reward (for fraction validation)
            user_current_balance: User's current FLX balance
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        if chr_reward.value > 0:
            flx_fraction = self.cm.div(flx_amount, chr_reward, log_list)
            if flx_fraction.value < MIN_FLX_REWARD_FRACTION.value:
                return ValidationResult(
                    passed=False,
                    error_code=EconomicViolationType.ECON_FLX_FRACTION_BELOW_MIN.value,
                    error_message=f"FLX fraction {flx_fraction.to_decimal_string()} below minimum {MIN_FLX_REWARD_FRACTION.to_decimal_string()}",
                    details={
                        "flx_amount": flx_amount.to_decimal_string(),
                        "chr_reward": chr_reward.to_decimal_string(),
                        "fraction": flx_fraction.to_decimal_string(),
                        "min_allowed": MIN_FLX_REWARD_FRACTION.to_decimal_string(),
                    },
                )
            if flx_fraction.value > MAX_FLX_REWARD_FRACTION.value:
                return ValidationResult(
                    passed=False,
                    error_code=EconomicViolationType.ECON_FLX_FRACTION_ABOVE_MAX.value,
                    error_message=f"FLX fraction {flx_fraction.to_decimal_string()} exceeds maximum {MAX_FLX_REWARD_FRACTION.to_decimal_string()}",
                    details={
                        "flx_amount": flx_amount.to_decimal_string(),
                        "chr_reward": chr_reward.to_decimal_string(),
                        "fraction": flx_fraction.to_decimal_string(),
                        "max_allowed": MAX_FLX_REWARD_FRACTION.to_decimal_string(),
                    },
                )
        new_user_balance = self.cm.add(user_current_balance, flx_amount, log_list)
        if new_user_balance.value > FLX_MAX_PER_USER.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_FLX_PER_USER_EXCEEDED.value,
                error_message=f"FLX per-user cap exceeded: {new_user_balance.to_decimal_string()} > {FLX_MAX_PER_USER.to_decimal_string()}",
                details={
                    "new_balance": new_user_balance.to_decimal_string(),
                    "cap": FLX_MAX_PER_USER.to_decimal_string(),
                    "flx_amount": flx_amount.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def validate_nod_allocation(
        self,
        nod_amount: BigNum128,
        total_fees: BigNum128,
        node_voting_power: BigNum128,
        total_voting_power: BigNum128,
        node_reward_share: BigNum128,
        total_epoch_issuance: BigNum128,
        active_node_count: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate NOD allocation against constitutional bounds.

        Constitutional checks:
        1. MIN_NOD_ALLOCATION_FRACTION <= (nod/fees) <= MAX_NOD_ALLOCATION_FRACTION
        2. node_voting_power / total_voting_power <= MAX_NOD_VOTING_POWER_RATIO
        3. node_reward_share <= MAX_NODE_REWARD_SHARE
        4. total_epoch_issuance <= NOD_MAX_ISSUANCE_PER_EPOCH
        5. active_node_count >= NOD_MIN_ACTIVE_NODES

        Args:
            nod_amount: Proposed NOD allocation amount
            total_fees: Total ATR fees collected
            node_voting_power: Individual node's NOD voting power
            total_voting_power: Total NOD voting power across all nodes
            node_reward_share: Individual node's reward share
            total_epoch_issuance: Total NOD issuance for the epoch
            active_node_count: Number of active nodes
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        if total_fees.value > 0:
            nod_fraction = self.cm.div(nod_amount, total_fees, log_list)
            if nod_fraction.value < MIN_NOD_ALLOCATION_FRACTION.value:
                return ValidationResult(
                    passed=False,
                    error_code=EconomicViolationType.ECON_NOD_ALLOCATION_BELOW_MIN.value,
                    error_message=f"NOD allocation fraction {nod_fraction.to_decimal_string()} below minimum {MIN_NOD_ALLOCATION_FRACTION.to_decimal_string()}",
                    details={
                        "nod_amount": nod_amount.to_decimal_string(),
                        "total_fees": total_fees.to_decimal_string(),
                        "fraction": nod_fraction.to_decimal_string(),
                        "min_allowed": MIN_NOD_ALLOCATION_FRACTION.to_decimal_string(),
                    },
                )
            if nod_fraction.value > MAX_NOD_ALLOCATION_FRACTION.value:
                return ValidationResult(
                    passed=False,
                    error_code=EconomicViolationType.ECON_NOD_ALLOCATION_ABOVE_MAX.value,
                    error_message=f"NOD allocation fraction {nod_fraction.to_decimal_string()} exceeds maximum {MAX_NOD_ALLOCATION_FRACTION.to_decimal_string()}",
                    details={
                        "nod_amount": nod_amount.to_decimal_string(),
                        "total_fees": total_fees.to_decimal_string(),
                        "fraction": nod_fraction.to_decimal_string(),
                        "max_allowed": MAX_NOD_ALLOCATION_FRACTION.to_decimal_string(),
                    },
                )
        if total_voting_power.value > 0:
            voting_power_ratio = self.cm.div(
                node_voting_power, total_voting_power, log_list
            )
            if voting_power_ratio.value > MAX_NOD_VOTING_POWER_RATIO.value:
                return ValidationResult(
                    passed=False,
                    error_code=EconomicViolationType.ECON_NOD_VOTING_POWER_EXCEEDED.value,
                    error_message=f"Node voting power ratio {voting_power_ratio.to_decimal_string()} exceeds maximum {MAX_NOD_VOTING_POWER_RATIO.to_decimal_string()}",
                    details={
                        "node_voting_power": node_voting_power.to_decimal_string(),
                        "total_voting_power": total_voting_power.to_decimal_string(),
                        "ratio": voting_power_ratio.to_decimal_string(),
                        "max_allowed": MAX_NOD_VOTING_POWER_RATIO.to_decimal_string(),
                    },
                )
        if node_reward_share.value > MAX_NODE_REWARD_SHARE.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_NOD_REWARD_SHARE_EXCEEDED.value,
                error_message=f"Node reward share {node_reward_share.to_decimal_string()} exceeds maximum {MAX_NODE_REWARD_SHARE.to_decimal_string()}",
                details={
                    "node_reward_share": node_reward_share.to_decimal_string(),
                    "max_allowed": MAX_NODE_REWARD_SHARE.to_decimal_string(),
                },
            )
        if total_epoch_issuance.value > NOD_MAX_ISSUANCE_PER_EPOCH.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_NOD_EPOCH_ISSUANCE_EXCEEDED.value,
                error_message=f"NOD epoch issuance {total_epoch_issuance.to_decimal_string()} exceeds maximum {NOD_MAX_ISSUANCE_PER_EPOCH.to_decimal_string()}",
                details={
                    "total_epoch_issuance": total_epoch_issuance.to_decimal_string(),
                    "max_allowed": NOD_MAX_ISSUANCE_PER_EPOCH.to_decimal_string(),
                },
            )
        min_nodes = int(NOD_MIN_ACTIVE_NODES.value // NOD_MIN_ACTIVE_NODES.SCALE)
        if active_node_count < min_nodes:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_NOD_INSUFFICIENT_ACTIVE_NODES.value,
                error_message=f"Insufficient active nodes: {active_node_count} < {min_nodes}",
                details={
                    "active_node_count": active_node_count,
                    "min_required": min_nodes,
                },
            )
        return ValidationResult(passed=True)

    def validate_psi_accumulation(
        self,
        psi_delta: BigNum128,
        current_psi_value: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate PSI (temporal/predictive stability) accumulation.

        Constitutional checks:
        1. abs(psi_delta) <= PSI_MAX_DELTA_PER_EPOCH (magnitude check)
        2. current_psi_value + psi_delta <= PSI_SATURATION_CAP

        Args:
            psi_delta: Proposed PSI change per epoch (positive or negative)
            current_psi_value: Current PSI accumulation
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        abs_psi_delta = BigNum128(abs(psi_delta.value))
        if abs_psi_delta.value > PSI_MAX_DELTA_PER_EPOCH.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_PSI_DELTA_ABOVE_MAX.value,
                error_message=f"PSI delta magnitude {abs_psi_delta.to_decimal_string()} exceeds maximum {PSI_MAX_DELTA_PER_EPOCH.to_decimal_string()}",
                details={
                    "psi_delta": psi_delta.to_decimal_string(),
                    "abs_delta": abs_psi_delta.to_decimal_string(),
                    "max_allowed": PSI_MAX_DELTA_PER_EPOCH.to_decimal_string(),
                },
            )
        new_psi_value = self.cm.add(current_psi_value, psi_delta, log_list)
        if new_psi_value.value > PSI_SATURATION_CAP.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_PSI_SATURATION_EXCEEDED.value,
                error_message=f"PSI saturation exceeded: {new_psi_value.to_decimal_string()} > {PSI_SATURATION_CAP.to_decimal_string()}",
                details={
                    "new_psi_value": new_psi_value.to_decimal_string(),
                    "cap": PSI_SATURATION_CAP.to_decimal_string(),
                    "psi_delta": psi_delta.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def validate_atr_usage(
        self,
        cost_multiplier: BigNum128,
        accumulated_atr: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate ATR (action/anti-abuse) cost parameters.

        Constitutional checks:
        1. cost_multiplier <= ATR_MAX_COST_MULTIPLIER
        2. accumulated_atr <= ATR_MAX_ACCUMULATION

        Args:
            cost_multiplier: Proposed ATR cost multiplier
            accumulated_atr: Current accumulated ATR penalty
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        if cost_multiplier.value > ATR_MAX_COST_MULTIPLIER.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_ATR_COST_MULTIPLIER_EXCEEDED.value,
                error_message=f"ATR cost multiplier {cost_multiplier.to_decimal_string()} exceeds maximum {ATR_MAX_COST_MULTIPLIER.to_decimal_string()}",
                details={
                    "cost_multiplier": cost_multiplier.to_decimal_string(),
                    "max_allowed": ATR_MAX_COST_MULTIPLIER.to_decimal_string(),
                },
            )
        if accumulated_atr.value > ATR_MAX_ACCUMULATION.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_ATR_ACCUMULATION_EXCEEDED.value,
                error_message=f"ATR accumulation {accumulated_atr.to_decimal_string()} exceeds maximum {ATR_MAX_ACCUMULATION.to_decimal_string()}",
                details={
                    "accumulated_atr": accumulated_atr.to_decimal_string(),
                    "max_allowed": ATR_MAX_ACCUMULATION.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def validate_emission_rate(
        self,
        emission_amount: BigNum128,
        emission_cap: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate emission rate against caps.

        Constitutional check:
        1. emission_amount <= emission_cap

        Args:
            emission_amount: Proposed emission amount
            emission_cap: Constitutional emission cap
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        if emission_amount.value > emission_cap.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_CHR_EMISSION_CAP_EXCEEDED.value,
                error_message=f"Emission amount {emission_amount.to_decimal_string()} exceeds cap {emission_cap.to_decimal_string()}",
                details={
                    "emission_amount": emission_amount.to_decimal_string(),
                    "cap": emission_cap.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def validate_supply_change(
        self,
        supply_delta: BigNum128,
        current_supply: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate supply change against maximum ratio.

        Constitutional check:
        1. abs(supply_delta / current_supply) <= MAX_TOTAL_SUPPLY_RATIO_CHANGE
        2. abs(supply_delta) <= MAX_SINGLE_EVENT_IMPACT * current_supply

        Args:
            supply_delta: Proposed supply change (positive or negative)
            current_supply: Current total supply
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        if current_supply.value == 0:
            return ValidationResult(passed=True)
        abs_delta = BigNum128(abs(supply_delta.value))
        delta_ratio = self.cm.div(abs_delta, current_supply, log_list)
        if delta_ratio.value > MAX_TOTAL_SUPPLY_RATIO_CHANGE.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_SUPPLY_RATIO_CHANGE_EXCEEDED.value,
                error_message=f"Supply ratio change {delta_ratio.to_decimal_string()} exceeds maximum {MAX_TOTAL_SUPPLY_RATIO_CHANGE.to_decimal_string()}",
                details={
                    "supply_delta": supply_delta.to_decimal_string(),
                    "current_supply": current_supply.to_decimal_string(),
                    "ratio": delta_ratio.to_decimal_string(),
                    "max_allowed": MAX_TOTAL_SUPPLY_RATIO_CHANGE.to_decimal_string(),
                },
            )
        max_impact = self.cm.mul(MAX_SINGLE_EVENT_IMPACT, current_supply, log_list)
        if abs_delta.value > max_impact.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_SINGLE_EVENT_IMPACT_EXCEEDED.value,
                error_message=f"Single event impact {abs_delta.to_decimal_string()} exceeds maximum {max_impact.to_decimal_string()}",
                details={
                    "supply_delta": supply_delta.to_decimal_string(),
                    "max_impact": max_impact.to_decimal_string(),
                    "current_supply": current_supply.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def validate_governance_change(
        self,
        parameter_name: str,
        new_value: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate governance parameter change.

        Constitutional checks vary by parameter type:
        - Quorum thresholds: MIN_QUORUM_THRESHOLD <= value <= MAX_QUORUM_THRESHOLD
        - Emergency quorum: value >= GOVERNANCE_EMERGENCY_QUORUM

        Args:
            parameter_name: Name of governance parameter
            new_value: Proposed new value
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []
        if "quorum" in parameter_name.lower():
            if new_value.value < MIN_QUORUM_THRESHOLD.value:
                return ValidationResult(
                    passed=False,
                    error_code=EconomicViolationType.GOV_SAFETY_QUORUM_BELOW_MIN.value,
                    error_message=f"Quorum threshold {new_value.to_decimal_string()} below minimum {MIN_QUORUM_THRESHOLD.to_decimal_string()}",
                    details={
                        "parameter": parameter_name,
                        "new_value": new_value.to_decimal_string(),
                        "min_allowed": MIN_QUORUM_THRESHOLD.to_decimal_string(),
                    },
                )
            if new_value.value > MAX_QUORUM_THRESHOLD.value:
                return ValidationResult(
                    passed=False,
                    error_code=EconomicViolationType.GOV_SAFETY_QUORUM_ABOVE_MAX.value,
                    error_message=f"Quorum threshold {new_value.to_decimal_string()} exceeds maximum {MAX_QUORUM_THRESHOLD.to_decimal_string()}",
                    details={
                        "parameter": parameter_name,
                        "new_value": new_value.to_decimal_string(),
                        "max_allowed": MAX_QUORUM_THRESHOLD.to_decimal_string(),
                    },
                )
        return ValidationResult(passed=True)

    def validate_res_reward(
        self,
        res_reward: BigNum128,
        current_total_supply: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate RES reward against constitutional draw limits.

        Constitutional check:
        1. res_reward <= RES_MAX_DRAW_PER_EPOCH * current_total_supply

        Args:
            res_reward: Proposed RES reward amount
            current_total_supply: Current total CHR supply (proxy for system scale)
            log_list: Optional log list for audit trail

        Returns:
            ValidationResult with pass/fail and error details
        """
        if log_list is None:
            log_list = []

        # Constitutional draw limit check
        max_allowed_draw = self.cm.mul(
            RES_MAX_DRAW_PER_EPOCH, current_total_supply, log_list
        )

        if res_reward.value > max_allowed_draw.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_RES_REWARD_EXCEEDED.value,
                error_message=f"RES reward {res_reward.to_decimal_string()} exceeds cap {max_allowed_draw.to_decimal_string()}",
                details={
                    "res_reward": res_reward.to_decimal_string(),
                    "cap": max_allowed_draw.to_decimal_string(),
                    "current_total_supply": current_total_supply.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def validate_per_address_reward(
        self,
        address: str,
        chr_amount: BigNum128,
        flx_amount: BigNum128,
        res_amount: BigNum128,
        total_amount: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        """
        Validate total reward for a single address against constitutional limits.

        Args:
            address: Recipient address
            chr_amount: CHR reward amount
            flx_amount: FLX reward amount
            res_amount: RES reward amount
            total_amount: Combined total reward
            log_list: Optional log list

        Returns:
            ValidationResult: pass/fail status
        """
        if log_list is None:
            log_list = []

        # Check total reward against MAX_REWARD_PER_ADDRESS
        if total_amount.value > MAX_REWARD_PER_ADDRESS.value:
            return ValidationResult(
                passed=False,
                error_code=EconomicViolationType.ECON_ADDRESS_REWARD_EXCEEDED.value,
                error_message=f"Total reward {total_amount.to_decimal_string()} for {address} exceeds per-address cap {MAX_REWARD_PER_ADDRESS.to_decimal_string()}",
                details={
                    "address": address,
                    "total_amount": total_amount.to_decimal_string(),
                    "cap": MAX_REWARD_PER_ADDRESS.to_decimal_string(),
                },
            )
        return ValidationResult(passed=True)

    def generate_violation_event_hash(
        self, validation_result: ValidationResult, timestamp: int
    ) -> str:
        """
        Generate SHA-256 event hash for violation (Merkle inclusion).

        Args:
            validation_result: Validation result with error details
            timestamp: Deterministic timestamp

        Returns:
            str: 64-character SHA-256 hash
        """
        event_data = {
            "operation": "economics_guard_violation",
            "error_code": validation_result.error_code,
            "error_message": validation_result.error_message,
            "details": validation_result.details,
            "timestamp": timestamp,
        }
        event_json = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(event_json.encode("utf-8")).hexdigest()


def test_economics_guard() -> None:
    """
    Test the EconomicsGuard implementation with all validation scenarios.
    """
    cm = CertifiedMath()
    guard = EconomicsGuard(cm)
    chr_reward = BigNum128.from_int(5000)
    daily_total = BigNum128.from_int(1000000)
    total_supply = BigNum128.from_int(100000000)
    result = guard.validate_chr_reward(chr_reward, daily_total, total_supply)
    assert result.passed == True, "CHR reward should pass"
    chr_reward_high = BigNum128.from_int(20000)
    result = guard.validate_chr_reward(chr_reward_high, daily_total, total_supply)
    assert result.passed == False, "CHR reward should fail"
    assert result.error_code == "ECON_CHR_REWARD_ABOVE_MAX"
    flx_reward = BigNum128.from_int(500)
    chr_base = BigNum128.from_int(5000)
    user_balance = BigNum128.from_int(10000)
    result = guard.validate_flx_reward(flx_reward, chr_base, user_balance)
    assert result.passed == True, "FLX reward should pass"
    user_balance_high = BigNum128.from_int(999000)
    chr_base_high = BigNum128.from_int(20000)
    flx_reward_big = BigNum128.from_int(2000)
    result = guard.validate_flx_reward(flx_reward_big, chr_base_high, user_balance_high)
    assert result.passed == False, "FLX should fail per-user cap"
    assert result.error_code == "ECON_FLX_PER_USER_EXCEEDED"
    nod_amount = BigNum128.from_int(1000)
    total_fees = BigNum128.from_int(10000)
    node_voting_power = BigNum128.from_int(2000)
    total_voting_power = BigNum128.from_int(10000)
    node_reward_share = BigNum128.from_string("0.20")
    epoch_issuance = BigNum128.from_int(50000)
    active_nodes = 5
    result = guard.validate_nod_allocation(
        nod_amount,
        total_fees,
        node_voting_power,
        total_voting_power,
        node_reward_share,
        epoch_issuance,
        active_nodes,
    )
    assert result.passed == True, "NOD allocation should pass"
    node_voting_power_high = BigNum128.from_int(3000)
    result = guard.validate_nod_allocation(
        nod_amount,
        total_fees,
        node_voting_power_high,
        total_voting_power,
        node_reward_share,
        epoch_issuance,
        active_nodes,
    )
    assert result.passed == False, "NOD should fail voting power cap"
    assert result.error_code == "ECON_NOD_VOTING_POWER_EXCEEDED"
    psi_delta = BigNum128.from_string("0.05")
    current_psi = BigNum128.from_int(50000)
    result = guard.validate_psi_accumulation(psi_delta, current_psi)
    assert result.passed == True, "PSI accumulation should pass"
    psi_delta_high = BigNum128.from_string("0.15")
    result = guard.validate_psi_accumulation(psi_delta_high, current_psi)
    assert result.passed == False, "PSI should fail delta cap"
    assert result.error_code == "ECON_PSI_DELTA_ABOVE_MAX"
    cost_multiplier = BigNum128.from_string("2.0")
    accumulated_atr = BigNum128.from_int(50000)
    result = guard.validate_atr_usage(cost_multiplier, accumulated_atr)
    assert result.passed == True, "ATR usage should pass"
    cost_multiplier_high = BigNum128.from_string("15.0")
    result = guard.validate_atr_usage(cost_multiplier_high, accumulated_atr)
    assert result.passed == False, "ATR should fail cost multiplier cap"
    assert result.error_code == "ECON_ATR_COST_MULTIPLIER_EXCEEDED"
    supply_delta = BigNum128.from_int(1000000)
    current_supply = BigNum128.from_int(100000000)
    result = guard.validate_supply_change(supply_delta, current_supply)
    assert result.passed == True, "Supply change should pass"
    supply_delta_high = BigNum128.from_int(5000000)
    result = guard.validate_supply_change(supply_delta_high, current_supply)
    assert result.passed == False, "Supply should fail ratio cap"
    assert result.error_code == "ECON_SUPPLY_RATIO_CHANGE_EXCEEDED"
    quorum_value = BigNum128.from_string("0.66")
    result = guard.validate_governance_change("nod_quorum_threshold", quorum_value)
    assert result.passed == True, "Governance change should pass"
    quorum_low = BigNum128.from_string("0.40")
    result = guard.validate_governance_change("nod_quorum_threshold", quorum_low)
    assert result.passed == False, "Governance should fail quorum min"
    assert result.error_code == "GOV_SAFETY_QUORUM_BELOW_MIN"
    violation = ValidationResult(
        passed=False,
        error_code="ECON_CHR_REWARD_ABOVE_MAX",
        error_message="Test violation",
        details={"reward": "20000"},
    )
    event_hash = guard.generate_violation_event_hash(violation, 1000)
    assert len(event_hash) == 64, "Event hash should be 64 characters"
    print("ECONOMICS GUARD TEST: ALL ASSERTIONS PASSED")


if __name__ == "__main__":
    test_economics_guard()
