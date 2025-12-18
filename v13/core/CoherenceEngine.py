"""
CoherenceEngine.py - QFS V13 Compliant Coherence Engine

Implements a stateless, deterministic coherence engine that operates only on
canonical TokenStateBundle inputs and uses only CertifiedMath for all calculations.
"""

import json
import hashlib
from typing import List, Dict, Any, Optional

try:
    from ..libs.CertifiedMath import CertifiedMath, BigNum128
    from .TokenStateBundle import TokenStateBundle
except ImportError:
    from v13.libs.CertifiedMath import CertifiedMath, BigNum128
    from v13.core.TokenStateBundle import TokenStateBundle
try:
    from v13.events.referral_events import ReferralRewarded
except ImportError:
    ReferralRewarded = Any


class CoherenceEngine:
    """
    QFS V13 Compliant Coherence Engine

    This is a pure, stateless validator that operates only on canonical TokenStateBundle inputs.
    All calculations use only CertifiedMath and BigNum128 for deterministic fixed-point arithmetic.
    No numpy, no time, no logging, no file I/O.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the QFS V13 Compliant Coherence Engine.

        Args:
            cm_instance: CertifiedMath instance for deterministic calculations
        """
        self.cm = cm_instance
        self.GOLDEN_RATIO_RECIPROCAL = BigNum128(618033988749894848)
        self.CLAMP_BOUND = BigNum128.from_int(10)
        self.ZERO = BigNum128.from_int(0)
        self.ONE = BigNum128.from_int(1)

    def calculate_modulator(
        self,
        I_vector: List[BigNum128],
        lambda_L: BigNum128,
        K: Optional[BigNum128] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> BigNum128:
        """
        Calculate modulator using CertifiedMath only.

        Args:
            I_vector: Integrated feedback vector as list of BigNum128
            lambda_L: Adaptive decay factor as BigNum128
            K: Clamping bound as BigNum128 (default: self.CLAMP_BOUND)
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            BigNum128: Modulator value
        """
        if K is None:
            K = self.CLAMP_BOUND
        if log_list is None:
            log_list = []
        proj_I = self.ZERO
        if len(I_vector) > 0:
            sum_I = self.ZERO
            for i in range(len(I_vector)):
                val = I_vector[i]
                sum_I = self.cm.add(sum_I, val, log_list, pqc_cid, quantum_metadata)
            length_bn = BigNum128.from_int(len(I_vector))
            proj_I = self.cm.div(sum_I, length_bn, log_list, pqc_cid, quantum_metadata)
        product = self.cm.mul(lambda_L, proj_I, log_list, pqc_cid, quantum_metadata)
        if self.cm.gt(product, K, log_list, pqc_cid, quantum_metadata):
            clamped_product = K
        else:
            clamped_product = product
        modulator_value = self.cm.exp(
            clamped_product, 50, log_list, pqc_cid, quantum_metadata
        )
        self.cm._log_operation(
            "calculate_modulator",
            {
                "I_vector_length": BigNum128.from_int(len(I_vector)),
                "lambda_L": lambda_L,
                "K": K,
                "product": product,
                "clamped_product": clamped_product,
            },
            modulator_value,
            log_list,
            pqc_cid,
            quantum_metadata,
        )
        return modulator_value

    def update_omega(
        self,
        features: List[BigNum128],
        I_vector: List[BigNum128],
        L: str,
        log_list: Optional[List[Dict[str, Any]]] = None,
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> List[BigNum128]:
        """
        Update Ω state vector using CertifiedMath only.

        Args:
            features: Feature vector as list of BigNum128
            I_vector: Integrated feedback vector as list of BigNum128
            L: Scale level identifier
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            List[BigNum128]: Updated Ω vector
        """
        if log_list is None:
            log_list = []
        normalized_features = features
        if len(features) > 0:
            sum_squares = self.ZERO
            for i in range(len(features)):
                val = features[i]
                val_squared = self.cm.mul(val, val, log_list, pqc_cid, quantum_metadata)
                sum_squares = self.cm.add(
                    sum_squares, val_squared, log_list, pqc_cid, quantum_metadata
                )
            norm = self.cm.sqrt(sum_squares, 50, log_list, pqc_cid, quantum_metadata)
            if self.cm.gt(norm, self.ZERO, log_list, pqc_cid, quantum_metadata):
                normalized_features = []
                for i in range(len(features)):
                    val = features[i]
                    normalized_val = self.cm.div(
                        val, norm, log_list, pqc_cid, quantum_metadata
                    )
                    normalized_features.append(normalized_val)
        lambda_L = self.GOLDEN_RATIO_RECIPROCAL
        modulator = self.calculate_modulator(
            I_vector,
            lambda_L,
            self.CLAMP_BOUND,
            log_list,
            pqc_cid,
            quantum_metadata,
            deterministic_timestamp,
        )
        updated_omega = []
        if len(normalized_features) > 0:
            for i in range(len(normalized_features)):
                val = normalized_features[i]
                omega_val = self.cm.mul(
                    val, modulator, log_list, pqc_cid, quantum_metadata
                )
                updated_omega.append(omega_val)
        if log_list is not None:
            omega_norm = self.ZERO
            if len(updated_omega) > 0:
                sum_squares = self.ZERO
                for i in range(len(updated_omega)):
                    val = updated_omega[i]
                    val_squared = self.cm.mul(
                        val, val, log_list, pqc_cid, quantum_metadata
                    )
                    sum_squares = self.cm.add(
                        sum_squares, val_squared, log_list, pqc_cid, quantum_metadata
                    )
                omega_norm = self.cm.sqrt(
                    sum_squares, 50, log_list, pqc_cid, quantum_metadata
                )
            self.cm._log_operation(
                "update_omega",
                {
                    "features_length": BigNum128.from_int(len(features)),
                    "I_vector_length": BigNum128.from_int(len(I_vector)),
                    "L": L,
                    "modulator": modulator,
                },
                omega_norm,
                log_list,
                pqc_cid,
                quantum_metadata,
            )
        return updated_omega

    def apply_hsmf_transition(
        self,
        current_bundle: TokenStateBundle,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        processed_events: Optional[List[Any]] = None,
    ) -> TokenStateBundle:
        """
        Apply HSMF transition to update all 5 tokens atomically.

        Args:
            current_bundle: Current TokenStateBundle
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            TokenStateBundle: Updated TokenStateBundle
        """
        c_holo = self._compute_c_holo(
            current_bundle, log_list, pqc_cid, quantum_metadata, deterministic_timestamp
        )
        C_MIN = BigNum128.from_int(1)
        if self.cm.lt(c_holo, C_MIN, log_list, pqc_cid, quantum_metadata):
            pass
        new_bundle = self._update_tokens(
            current_bundle,
            c_holo,
            log_list,
            pqc_cid,
            quantum_metadata,
            deterministic_timestamp,
            processed_events,
        )
        self.cm._log_operation(
            "apply_hsmf_transition",
            {
                "bundle_id": current_bundle.bundle_id,
                "timestamp": BigNum128.from_int(deterministic_timestamp),
            },
            c_holo,
            log_list,
            pqc_cid,
            quantum_metadata,
        )
        return new_bundle

    def _compute_c_holo(
        self,
        current_bundle: TokenStateBundle,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ) -> BigNum128:
        """
        Compute C_holo attractor logic using only the most recent TokenState snapshot.

        Args:
            current_bundle: Current TokenStateBundle
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            BigNum128: C_holo value
        """
        s_chr = current_bundle.get_coherence_metric()
        s_flx = current_bundle.get_flux_metric()
        s_psi_sync = current_bundle.get_psi_sync_metric()
        s_res = current_bundle.get_resonance_metric()
        s_atr = current_bundle.get_atr_metric()
        sum_dissonance = self.cm.add(s_res, s_flx, log_list, pqc_cid, quantum_metadata)
        sum_dissonance = self.cm.add(
            sum_dissonance, s_psi_sync, log_list, pqc_cid, quantum_metadata
        )
        one_plus_dissonance = self.cm.add(
            self.ONE, sum_dissonance, log_list, pqc_cid, quantum_metadata
        )
        c_holo = self.cm.div(
            self.ONE, one_plus_dissonance, log_list, pqc_cid, quantum_metadata
        )
        self.cm._log_operation(
            "compute_c_holo",
            {
                "s_res": s_res,
                "s_flx": s_flx,
                "s_psi_sync": s_psi_sync,
                "sum_dissonance": sum_dissonance,
            },
            c_holo,
            log_list,
            pqc_cid,
            quantum_metadata,
        )
        return c_holo

    def _update_tokens(
        self,
        current_bundle: TokenStateBundle,
        c_holo: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
        processed_events: Optional[List[Any]] = None,
    ) -> TokenStateBundle:
        """
        Update all 5 tokens atomically based on C_holo.

        Args:
            current_bundle: Current TokenStateBundle
            c_holo: Computed C_holo value
            log_list: Audit log list for deterministic operations
            pqc_cid: PQC correlation ID for audit trail
            quantum_metadata: Quantum metadata for audit trail
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            TokenStateBundle: Updated TokenStateBundle
        """
        new_flx_state = dict(current_bundle.flx_state)
        if processed_events:
            # Sort events deterministically by timestamp, then event_id for replay consistency
            sorted_events = sorted(
                processed_events,
                key=lambda e: (
                    getattr(e, "timestamp", 0),
                    getattr(e, "event_id", "") if hasattr(e, "event_id") else str(e),
                ),
            )
            for event in sorted_events:
                if (
                    hasattr(event, "event_type")
                    and event.event_type == "REFERRAL_REWARDED"
                ):
                    wallet = event.referrer_wallet
                    amount = BigNum128.from_int(event.amount_scaled)
                    token_type = getattr(event, "token_type", "FLX")
                    if token_type == "FLX":
                        current_balance = new_flx_state.get(
                            wallet, BigNum128.from_int(0)
                        )
                        if not isinstance(current_balance, BigNum128):
                            pass
                        new_balance = self.cm.add(
                            current_balance, amount, log_list, pqc_cid, quantum_metadata
                        )
                        new_flx_state[wallet] = new_balance
                        self.cm._log_operation(
                            "apply_referral_reward",
                            {"wallet": wallet, "amount": amount},
                            new_balance,
                            log_list,
                            pqc_cid,
                            quantum_metadata,
                        )
        self.cm._log_operation(
            "update_tokens",
            {
                "bundle_id": current_bundle.bundle_id,
                "c_holo": c_holo,
                "events_processed": len(processed_events) if processed_events else 0,
            },
            c_holo,
            log_list,
            pqc_cid,
            quantum_metadata,
        )
        from v13.core.TokenStateBundle import create_token_state_bundle

        return create_token_state_bundle(
            chr_state=current_bundle.chr_state,
            flx_state=new_flx_state,
            psi_sync_state=current_bundle.psi_sync_state,
            atr_state=current_bundle.atr_state,
            res_state=current_bundle.res_state,
            nod_state=current_bundle.nod_state,
            lambda1=current_bundle.lambda1,
            lambda2=current_bundle.lambda2,
            c_crit=current_bundle.c_crit,
            pqc_cid=pqc_cid or current_bundle.pqc_cid,
            timestamp=deterministic_timestamp or current_bundle.timestamp,
            storage_metrics=current_bundle.storage_metrics,
            quantum_metadata=quantum_metadata or current_bundle.quantum_metadata,
            parameters=current_bundle.parameters,
        )
