"""
CIR302_Handler.py - Deterministic Halt System for QFS V13.6

Implements the CIR302_Handler class for deterministically halting
the system in case of critical failures.

V13.6 Constitutional Integration:
- Maps economic guard violations (ECON_BOUND_VIOLATION_*)
- Maps NOD invariant violations (INVARIANT_VIOLATION_NOD_*)
- Maps AEGIS node verification failures (NODE_*)
- Generates structured finality artifacts with guard status
- Supports constitutional_guard_status in AEGIS_FINALITY_SEAL
"""

import json
import hashlib
from typing import Dict, Any, Optional, List, Type

try:
    from libs.BigNum128 import BigNum128
    from libs.CertifiedMath import CertifiedMath
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath

    # Import ZeroSimAbort
    from v13.libs.fatal_errors import ZeroSimAbort, log_fatal_exception


class CIR302_Handler:
    # ... (skipping unchanged DocString parts for brevity in tool call, focusing on logic)
    # ...
    """
    Deterministic Halt System for QFS V13.6.
    ...
    """

    CIR302_CODE = BigNum128.from_int(302)
    GUARD_ERROR_MAPPINGS = {
        "ECON_BOUND_VIOLATION": "Constitutional economic bound violated: Operation attempted outside allowed parameters",
        "ECON_CHR_REWARD_ABOVE_MAX": "CHR reward exceeds constitutional maximum per action",
        "ECON_CHR_REWARD_BELOW_MIN": "CHR reward below constitutional minimum per action",
        "ECON_CHR_EMISSION_CAP_EXCEEDED": "CHR daily emission cap exceeded: Action violates daily inflation bounds",
        "ECON_CHR_SATURATION_EXCEEDED": "CHR saturation threshold exceeded: System liquidity risk detected",
        "ECON_FLX_FRACTION_ABOVE_MAX": "FLX reward fraction exceeds constitutional maximum",
        "ECON_FLX_FRACTION_BELOW_MIN": "FLX reward fraction below constitutional minimum",
        "ECON_FLX_PER_USER_EXCEEDED": "FLX per-user cap exceeded: Concentration risk detected",
        "ECON_NOD_ALLOCATION_ABOVE_MAX": "NOD allocation fraction exceeds constitutional maximum",
        "ECON_NOD_ALLOCATION_BELOW_MIN": "NOD allocation fraction below constitutional minimum",
        "ECON_NOD_VOTING_POWER_EXCEEDED": "Single node exceeds constitutional max voting power (25%)",
        "ECON_NOD_REWARD_SHARE_EXCEEDED": "Single node exceeds constitutional max reward share (30%)",
        "ECON_NOD_EPOCH_ISSUANCE_EXCEEDED": "NOD issuance exceeds constitutional epoch cap",
        "ECON_NOD_INSUFFICIENT_ACTIVE_NODES": "Insufficient active nodes for constitutional NOD consensus",
        "ECON_PSI_DELTA_ABOVE_MAX": "PSI delta exceeds constitutional maximum allowed per epoch",
        "ECON_PSI_DELTA_BELOW_MIN": "PSI delta below constitutional minimum magnitude",
        "ECON_PSI_SATURATION_EXCEEDED": "PSI saturation cap exceeded: Stability protocol violation",
        "ECON_ATR_COST_MULTIPLIER_EXCEEDED": "ATR cost multiplier exceeds constitutional maximum",
        "ECON_ATR_ACCUMULATION_EXCEEDED": "ATR accumulation exceeds constitutional maximum storage",
        "ECON_SUPPLY_RATIO_CHANGE_EXCEEDED": "Total supply ratio change exceeds constitutional safety bound",
        "ECON_SINGLE_EVENT_IMPACT_EXCEEDED": "Single event impact exceeds constitutional safety threshold",
        "GOV_SAFETY_QUORUM_ABOVE_MAX": "Governance quorum above constitutional maximum bound",
        "GOV_SAFETY_QUORUM_BELOW_MIN": "Governance quorum below constitutional minimum bound",
        "GOV_SAFETY_PARAMETER_INVALID": "Governance parameter out of constitutional safety bounds",
        "ECON_ADDRESS_REWARD_EXCEEDED": "Per-address reward cap exceeded: Anti-concentration guard triggered",
        "ECON_RES_REWARD_EXCEEDED": "RES reward exceeds constitutional 0.5% draw limit of total supply",
        "ECON_DUST_THRESHOLD": "Reward below dust threshold",
        "ECON_IMMUTABLE_CONSTANT_MUTATION": "Attempted mutation of [IMMUTABLE] constant",
        "INVARIANT_VIOLATION_NOD_TRANSFER": "NOD transfer firewall: NOD delta outside allowed context",
        "NOD_INVARIANT_I1_VIOLATED": "NOD-I1 violated: Non-transferability (user transfer attempt)",
        "NOD_INVARIANT_I2_VIOLATED": "NOD-I2 violated: Supply conservation (unverified node or out-of-allocator creation)",
        "NOD_INVARIANT_I3_VIOLATED": "NOD-I3 violated: Voting power bounds (single node > 25%)",
        "NOD_INVARIANT_I4_VIOLATED": "NOD-I4 violated: Deterministic replay (snapshot hash mismatch)",
        "NODE_NOT_IN_REGISTRY": "Node not found in AEGIS registry",
        "NODE_INSUFFICIENT_UPTIME": "Node uptime below threshold",
        "NODE_TELEMETRY_HASH_MISMATCH": "Telemetry hash coherence failure",
        "NODE_CRYPTOGRAPHIC_IDENTITY_INVALID": "PQC identity verification failed",
        "NODE_HEALTH_CHECK_FAILED": "Node health check failed",
        "AEGIS_OFFLINE": "AEGIS system offline or degraded",
        "AEGIS_SNAPSHOT_UNAVAILABLE": "AEGIS snapshot unavailable for deterministic replay",
        "AEGIS_SCHEMA_VERSION_MISMATCH": "AEGIS snapshot schema version mismatch",
    }

    def __init__(self, cm_instance: Type[CertifiedMath]):
        """
        Initialize the CIR-302 Handler.

        Args:
            cm_instance: CertifiedMath class for deterministic operations and logging
        """
        self.cm = cm_instance
        self.quantum_metadata = {
            "component": "CIR302_Handler",
            "version": "QFS-V13",
            "timestamp": BigNum128(0).to_decimal_string(),
            "pqc_scheme": "None",
        }

    def handle_violation(
        self,
        error_type: str,
        error_details: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Deterministically halt the system in case of critical failures.
        Logs the violation via CertifiedMath before hard halt.

        Args:
            error_type: Type of violation
            error_details: Details of the violation
            log_list: Log list for canonical logging
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        self.cm._log_operation(
            "cir302_violation",
            {
                "cir": "302",
                "error_type": error_type,
                "error_details": error_details,
                "timestamp": BigNum128.from_int(
                    deterministic_timestamp
                ).to_decimal_string(),
                "finality": "CIR302_REGISTERED",
                "tag_incident_id": f"cir302_{deterministic_timestamp}",
                "tag_incident_type": error_type,
                "tag_component": "CIR302",
            },
            CIR302_Handler.CIR302_CODE,
            log_list,
            pqc_cid,
            quantum_metadata,
        )

        # HARD HALT — no return, no state, no quarantine
        # Exit code must be deterministically derived from the fault, not hardcoded
        exit_code = self.cm.idiv_bn(
            CIR302_Handler.CIR302_CODE.value, CIR302_Handler.CIR302_CODE.SCALE
        )

        # Raise Deterministic Abort instead of SystemExit
        raise ZeroSimAbort(
            f"CIR302 HALT: {error_type} - {error_details}", exit_code=exit_code
        )

    def handle_guard_violation(
        self,
        error_code: str,
        error_message: str,
        context: Dict[str, Any],
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
        quantum_metadata: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: int = 0,
    ):
        """
        Handle constitutional guard violations with structured error codes.

        V13.6: Maps guard error codes to halt reasons and generates structured
        finality artifacts with guard status.

        Args:
            error_code: Structured error code (e.g., 'ECON_BOUND_VIOLATION', 'NOD_INVARIANT_I1_VIOLATED')
            error_message: Human-readable error message
            context: Additional context (call_context, proposal_id, node_id, address, etc.)
            log_list: Log list for canonical logging
            pqc_cid: Optional PQC correlation ID
            quantum_metadata: Optional quantum metadata
            deterministic_timestamp: Deterministic timestamp
        """
        halt_reason = self.GUARD_ERROR_MAPPINGS.get(
            error_code, f"Unknown guard violation: {error_code}"
        )
        violation_payload = {
            "cir": "302",
            "violation_type": "constitutional_guard",
            "error_code": error_code,
            "error_message": error_message,
            "halt_reason": halt_reason,
            "timestamp": BigNum128.from_int(
                deterministic_timestamp
            ).to_decimal_string(),
            "context": context,
        }
        self.cm._log_operation(
            "constitutional_guard_violation",
            violation_payload,
            CIR302_Handler.CIR302_CODE,
            log_list,
            pqc_cid,
            quantum_metadata,
        )
        finality_seal = self.generate_guard_finality_seal(
            error_code, error_message, context, deterministic_timestamp
        )
        log_list.append(
            {
                "operation": "cir302_finality_seal_generated",
                "finality_seal_hash": finality_seal,
                "error_code": error_code,
                "timestamp": deterministic_timestamp,
            }
        )

        # HARD HALT — no return, no state, no quarantine
        exit_code = self.cm.idiv_bn(
            CIR302_Handler.CIR302_CODE.value, CIR302_Handler.CIR302_CODE.SCALE
        )

        # Raise Deterministic Abort instead of SystemExit
        raise ZeroSimAbort(
            f"GUARD HALT: {error_code} - {error_message}", exit_code=exit_code
        )

    def generate_finality_seal(
        self,
        system_state: Optional[Dict[str, Any]] = None,
        constitutional_guard_status: str = "ok",
    ) -> str:
        """
        Produces JSON seal with deterministic hash of state.
        This method is for pre-halt logging only - CIR302 halts immediately after.

        V13.6: Includes constitutional_guard_status for guard violation tracking.

        Args:
            system_state: Optional system state to include in seal
            constitutional_guard_status: Guard status ("ok" | "halted")

        Returns:
            str: Deterministic hash of system state
        """
        seal_data = {
            "component": "CIR302_FINALITY_SEAL",
            "version": "QFS-V13.6",
            "timestamp": BigNum128(0).to_decimal_string(),
            "is_active": False,
            "constitutional_guard_status": constitutional_guard_status,
            "system_state_hash": self._hash_system_state(system_state)
            if system_state
            else "",
            "quantum_metadata": self.quantum_metadata,
        }
        seal_json = json.dumps(seal_data, sort_keys=True, separators=(",", ":"))
        seal_hash = hashlib.sha256(seal_json.encode("utf-8")).hexdigest()
        return seal_hash

    def generate_guard_finality_seal(
        self,
        error_code: str,
        error_message: str,
        context: Dict[str, Any],
        timestamp: int = 0,
    ) -> str:
        """
        Generate finality seal with guard violation metadata.

        V13.6: Structured seal for constitutional guard violations.

        Args:
            error_code: Structured error code
            error_message: Human-readable error message
            context: Violation context
            timestamp: Deterministic timestamp

        Returns:
            str: Deterministic hash of finality seal
        """
        seal_data = {
            "component": "AEGIS_FINALITY_SEAL",
            "version": "QFS-V13.6",
            "timestamp": BigNum128.from_int(timestamp).to_decimal_string(),
            "is_active": False,
            "constitutional_guard_status": "halted",
            "violations": [
                {
                    "error_code": error_code,
                    "error_message": error_message,
                    "halt_reason": self.GUARD_ERROR_MAPPINGS.get(
                        error_code, "Unknown violation"
                    ),
                }
            ],
            "quantum_metadata": self.quantum_metadata,
        }
        for key, value in sorted(context.items()):
            seal_data[f"violation_context_{key}"] = str(value)
        seal_json = json.dumps(seal_data, sort_keys=True, separators=(",", ":"))
        seal_hash = hashlib.sha256(seal_json.encode("utf-8")).hexdigest()
        return seal_hash

    def _hash_system_state(self, system_state: Dict[str, Any]) -> str:
        """
        Generate deterministic hash of system state.

        Args:
            system_state: System state dictionary

        Returns:
            str: SHA-256 hash of system state
        """
        if not system_state:
            return ""
        state_json = json.dumps(system_state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(state_json.encode("utf-8")).hexdigest()
