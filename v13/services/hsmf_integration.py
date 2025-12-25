"""
hsmf_integration.py - AEGIS → HSMF → RewardAllocator Integration Service

Provides a hardened integration layer that:
1. Receives action requests from AEGIS
2. Computes HSMF metrics (action cost, c_holo, rewards)
3. Emits HSMFProof for auditing
4. Passes reward allocations to RewardAllocator

This module is Zero-Sim compliant and maintains full determinism.

References:
    - docs/HSMF_MathContracts.md
    - docs/hsmf_harmonic_design.md
    - core/HSMF.py (HSMFProof)
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

try:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.core.HSMF import HSMF, HSMFProof, ValidationResult
    from v13.core.TokenStateBundle import TokenStateBundle
    from v13.libs.governance.RewardAllocator import RewardAllocator, AllocatedReward
    from v13.core.reward_types import RewardBundle
except ImportError:
    from libs.BigNum128 import BigNum128
    from libs.CertifiedMath import CertifiedMath
    from core.HSMF import HSMF, HSMFProof, ValidationResult
    from core.TokenStateBundle import TokenStateBundle
    from libs.governance.RewardAllocator import RewardAllocator, AllocatedReward
    from core.reward_types import RewardBundle


@dataclass
class HSMFActionResult:
    """
    Result from HSMF action processing.

    Contains all computed metrics, proof record, and allocation results.
    """

    # Identifiers
    action_id: str
    user_id: str

    # HSMF Metrics
    action_cost: BigNum128
    c_holo: BigNum128

    # Per-token rewards
    chr_reward: BigNum128
    flx_reward: BigNum128
    res_reward: BigNum128
    psi_sync_reward: BigNum128
    atr_reward: BigNum128
    total_reward: BigNum128

    # Proof and validation
    proof: HSMFProof
    is_valid: bool
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action_id": self.action_id,
            "user_id": self.user_id,
            "action_cost": self.action_cost.to_decimal_string(),
            "c_holo": self.c_holo.to_decimal_string(),
            "chr_reward": self.chr_reward.to_decimal_string(),
            "flx_reward": self.flx_reward.to_decimal_string(),
            "res_reward": self.res_reward.to_decimal_string(),
            "psi_sync_reward": self.psi_sync_reward.to_decimal_string(),
            "atr_reward": self.atr_reward.to_decimal_string(),
            "total_reward": self.total_reward.to_decimal_string(),
            "is_valid": self.is_valid,
            "errors": self.errors,
        }


class HSMFIntegrationService:
    """
    Integration service for AEGIS → HSMF → RewardAllocator flow.

    This service:
    1. Receives action requests with token bundle and metrics
    2. Computes HSMF action cost and coherence coefficient
    3. Calculates per-token reward allocations
    4. Emits structured HSMFProof for auditing
    5. Optionally routes to RewardAllocator for distribution

    All operations are deterministic and Zero-Sim compliant.
    """

    HSMF_VERSION = "v13.5"

    def __init__(
        self,
        cm_instance: CertifiedMath,
        reward_allocator: Optional[RewardAllocator] = None,
    ):
        """
        Initialize the HSMF Integration Service.

        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            reward_allocator: Optional RewardAllocator for distribution
        """
        self.cm = cm_instance
        self.hsmf = HSMF(cm_instance)
        self.reward_allocator = reward_allocator
        self.ONE = BigNum128.from_int(1)
        self.ZERO = BigNum128.from_int(0)

    def process_action(
        self,
        action_id: str,
        user_id: str,
        s_res: BigNum128,
        s_flx: BigNum128,
        s_psi_sync: BigNum128,
        f_atr: BigNum128,
        s_chr: BigNum128,
        lambda1: BigNum128,
        lambda2: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> HSMFActionResult:
        """
        Process an action through HSMF and compute all metrics.

        Args:
            action_id: Unique action identifier
            user_id: User/wallet identifier
            s_res: Resistance metric
            s_flx: Flux deviation metric
            s_psi_sync: Psi sync deviation metric
            f_atr: ATR factor
            s_chr: Coherence metric
            lambda1: Flux weight
            lambda2: Psi sync weight
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata

        Returns:
            HSMFActionResult with all computed metrics and proof
        """
        errors: List[str] = []
        is_valid = True

        # Compute action cost
        action_cost = self.hsmf._calculate_action_cost_qfs(
            s_res,
            s_flx,
            s_psi_sync,
            f_atr,
            lambda1,
            lambda2,
            log_list,
            quantum_metadata,
            pqc_cid,
        )

        # Compute c_holo (coherence coefficient)
        c_holo = self.hsmf._calculate_c_holo(
            s_res, s_flx, s_psi_sync, log_list, quantum_metadata, pqc_cid
        )

        # Validate c_holo bounds
        if c_holo.value > self.ONE.value:
            errors.append("c_holo exceeds upper bound (1.0)")
            is_valid = False
        if c_holo.value <= 0:
            errors.append("c_holo must be positive")
            is_valid = False

        # Build metrics dict for reward computation
        metrics = {
            "s_chr": s_chr,
            "c_holo": c_holo,
            "s_res": s_res,
            "s_flx": s_flx,
            "s_psi_sync": s_psi_sync,
            "f_atr": f_atr,
            "action_cost": action_cost,
        }

        # Compute rewards
        rewards = self.hsmf._compute_hsmf_rewards(
            metrics, log_list, pqc_cid, quantum_metadata
        )

        # Create proof record
        proof = HSMFProof(
            action_id=action_id,
            user_id=user_id,
            s_res=s_res.to_decimal_string(),
            s_flx=s_flx.to_decimal_string(),
            s_psi_sync=s_psi_sync.to_decimal_string(),
            f_atr=f_atr.to_decimal_string(),
            s_chr=s_chr.to_decimal_string(),
            lambda1=lambda1.to_decimal_string(),
            lambda2=lambda2.to_decimal_string(),
            action_cost=action_cost.to_decimal_string(),
            c_holo=c_holo.to_decimal_string(),
            chr_reward=rewards["chr_reward"].to_decimal_string(),
            flx_reward=rewards["flx_reward"].to_decimal_string(),
            res_reward=rewards["res_reward"].to_decimal_string(),
            psi_sync_reward=rewards["psi_sync_reward"].to_decimal_string(),
            atr_reward=rewards["atr_reward"].to_decimal_string(),
            total_reward=rewards["total_reward"].to_decimal_string(),
            hsmf_version=self.HSMF_VERSION,
        )

        # Emit proof to log
        self.hsmf._emit_hsmf_poe(proof, log_list)

        # Log integration event
        self.cm._log_operation(
            "hsmf_integration_complete",
            {"action_id": action_id, "is_valid": "true" if is_valid else "false"},
            action_cost,
            log_list,
            pqc_cid,
            quantum_metadata,
        )

        return HSMFActionResult(
            action_id=action_id,
            user_id=user_id,
            action_cost=action_cost,
            c_holo=c_holo,
            chr_reward=rewards["chr_reward"],
            flx_reward=rewards["flx_reward"],
            res_reward=rewards["res_reward"],
            psi_sync_reward=rewards["psi_sync_reward"],
            atr_reward=rewards["atr_reward"],
            total_reward=rewards["total_reward"],
            proof=proof,
            is_valid=is_valid,
            errors=errors,
        )

    def process_action_from_bundle(
        self,
        action_id: str,
        user_id: str,
        token_bundle: TokenStateBundle,
        f_atr: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
    ) -> HSMFActionResult:
        """
        Process an action using a TokenStateBundle.

        Extracts metrics from the bundle and delegates to process_action.

        Args:
            action_id: Unique action identifier
            user_id: User/wallet identifier
            token_bundle: Token state bundle with all metrics
            f_atr: ATR factor
            log_list: Audit log list
            pqc_cid: PQC correlation ID
            quantum_metadata: Quantum metadata

        Returns:
            HSMFActionResult with all computed metrics and proof
        """
        # Extract metrics from bundle
        s_chr = token_bundle.get_coherence_metric()
        s_res = self.hsmf._calculate_I_eff(
            s_chr,
            token_bundle.parameters.get("beta_penalty", BigNum128.from_int(100000000)),
            log_list,
            quantum_metadata,
            pqc_cid,
        )
        s_flx = self.hsmf._calculate_delta_lambda(
            token_bundle.flx_state,
            token_bundle.parameters.get("phi", self.hsmf.PHI),
            log_list,
            quantum_metadata,
            pqc_cid,
        )
        s_psi_sync = self.hsmf._calculate_delta_h(
            token_bundle.psi_sync_state,
            BigNum128.from_int(0),  # Reference value
            log_list,
            quantum_metadata,
            pqc_cid,
        )

        return self.process_action(
            action_id=action_id,
            user_id=user_id,
            s_res=s_res,
            s_flx=s_flx,
            s_psi_sync=s_psi_sync,
            f_atr=f_atr,
            s_chr=s_chr,
            lambda1=token_bundle.lambda1,
            lambda2=token_bundle.lambda2,
            log_list=log_list,
            pqc_cid=pqc_cid,
            quantum_metadata=quantum_metadata,
        )
