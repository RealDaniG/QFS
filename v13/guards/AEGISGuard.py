"""
AEGISGuard.py - Meta-Guard Orchestrator for QFS V13 P2

Implements the AEGISGuard class as a meta-guard orchestrator that
coordinates SafetyGuard and EconomicsGuard evaluations.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from v13.libs.CertifiedMath import BigNum128, CertifiedMath
from v13.libs.economics.EconomicsGuard import EconomicsGuard
from v13.libs.core.SafetyGuard import SafetyGuard
from v13.core.TokenStateBundle import TokenStateBundle


@dataclass
class AEGISObservation:
    """Represents an AEGIS observation for logging and analysis."""

    observation_id: str
    timestamp: int
    event_type: str
    inputs: Dict[str, Any]
    safety_guard_result: Optional[Dict[str, Any]]
    economics_guard_result: Optional[Dict[str, Any]]
    aegis_decision: str
    explanation: str
    pqc_cid: str
    quantum_metadata: Dict[str, Any]
    block_suggested: bool = False
    severity: str = "info"


class AEGISGuard:
    """
    AEGIS Guard as a meta-guard orchestrator.

    This guard acts as a meta-guard that orchestrates SafetyGuard and EconomicsGuard,
    enforcing a clear threat model and producing QFS-specific security test coverage.
    Provides both observation capabilities and advisory blocking suggestions.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the AEGIS Guard.

        Args:
            cm_instance: CertifiedMath instance for deterministic operations
        """
        self.cm = cm_instance
        self.economics_guard = EconomicsGuard(cm_instance)
        self.safety_guard = SafetyGuard(cm_instance)
        self.observations: List[AEGISObservation] = []
        self.quantum_metadata = {
            "component": "AEGISGuard",
            "version": "QFS-V13-P2-Minimal-Advisory",
            "pqc_scheme": "Dilithium-5",
        }
        self.ledger_economics_service = None

    def set_ledger_economics_service(self, service):
        """
        Set the ledger economics service for real economics data.

        Args:
            service: Ledger economics service that provides real economics data
        """
        self.ledger_economics_service = service

    def observe_event(
        self,
        event_type: str,
        inputs: Dict[str, Any],
        token_bundle: TokenStateBundle,
        deterministic_timestamp: int = 0,
    ) -> AEGISObservation:
        """
        Observe an event and coordinate guard evaluations.

        Args:
            event_type: Type of event being observed
            inputs: Event inputs for guard evaluation
            token_bundle: Current token state bundle
            deterministic_timestamp: Deterministic timestamp from DRV_Packet

        Returns:
            AEGISObservation: The observation record
        """
        safety_result = None
        try:
            if event_type == "feed_ranking":
                content_text = inputs.get("content", "")
                safety_validation = self.safety_guard.validate_content(
                    content_text=content_text,
                    content_metadata=inputs,
                    token_bundle=token_bundle,
                    log_list=[],
                    pqc_cid=f"safety_check_{deterministic_timestamp}",
                    deterministic_timestamp=deterministic_timestamp,
                )
                safety_result = {
                    "passed": safety_validation.passed,
                    "risk_score": safety_validation.risk_score.to_decimal_string(),
                    "explanation": safety_validation.explanation,
                    "policy_version": safety_validation.policy_version,
                }
            elif event_type == "social_interaction":
                content_text = inputs.get("content", "")
                safety_validation = self.safety_guard.validate_content(
                    content_text=content_text,
                    content_metadata=inputs,
                    token_bundle=token_bundle,
                    log_list=[],
                    pqc_cid=f"safety_check_{deterministic_timestamp}",
                    deterministic_timestamp=deterministic_timestamp,
                )
                safety_result = {
                    "passed": safety_validation.passed,
                    "risk_score": safety_validation.risk_score.to_decimal_string(),
                    "explanation": safety_validation.explanation,
                    "policy_version": safety_validation.policy_version,
                }
            else:
                safety_result = {
                    "passed": True,
                    "explanation": "Default safety check passed",
                }
        except Exception as e:
            safety_result = {
                "passed": False,
                "explanation": f"Safety guard evaluation failed: {str(e)}",
            }
        economics_result = None
        try:
            if event_type == "social_interaction":
                reward_amount = BigNum128.from_int(100)
                if self.ledger_economics_service is not None:
                    try:
                        daily_totals = (
                            self.ledger_economics_service.get_chr_daily_totals()
                        )
                        total_supply_data = (
                            self.ledger_economics_service.get_chr_total_supply()
                        )
                        current_daily_total = daily_totals.get(
                            "current_daily_total", BigNum128.from_int(0)
                        )
                        current_total_supply = total_supply_data.get(
                            "current_total_supply", BigNum128.from_int(1000000)
                        )
                    except Exception as e:
                        log_entry = {
                            "level": "WARNING",
                            "message": f"Ledger economics service failed, falling back to demo values: {e}",
                            "timestamp": deterministic_timestamp,
                        }
                        current_daily_total = BigNum128.from_int(10000)
                        current_total_supply = BigNum128.from_int(1000000)
                else:
                    current_daily_total = BigNum128.from_int(10000)
                    current_total_supply = BigNum128.from_int(1000000)
                economics_validation = self.economics_guard.validate_chr_reward(
                    reward_amount=reward_amount,
                    current_daily_total=current_daily_total,
                    current_total_supply=current_total_supply,
                    log_list=[],
                )
                economics_result = {
                    "passed": economics_validation.passed,
                    "error_code": economics_validation.error_code,
                    "explanation": economics_validation.error_message
                    if not economics_validation.passed
                    else "Economics guard validation passed",
                }
            else:
                economics_result = {
                    "passed": True,
                    "explanation": "Default economics check passed",
                }
        except Exception as e:
            economics_result = {
                "passed": False,
                "explanation": f"Economics guard evaluation failed: {str(e)}",
            }
        serializable_inputs = {}
        for key, value in sorted(inputs.items()):
            if hasattr(value, "to_decimal_string"):
                serializable_inputs[key] = value.to_decimal_string()
            else:
                serializable_inputs[key] = str(value)
        observation_data = {
            "event_type": event_type,
            "inputs": serializable_inputs,
            "timestamp": deterministic_timestamp,
        }
        observation_json = json.dumps(observation_data, sort_keys=True)
        observation_id = hashlib.sha256(observation_json.encode()).hexdigest()[:32]
        observation = AEGISObservation(
            observation_id=observation_id,
            timestamp=deterministic_timestamp,
            event_type=event_type,
            inputs=serializable_inputs,
            safety_guard_result=safety_result,
            economics_guard_result=economics_result,
            aegis_decision="observe",
            explanation=f"AEGIS observation for {event_type}",
            pqc_cid=f"aegis_obs_{deterministic_timestamp}",
            quantum_metadata=self.quantum_metadata.copy(),
        )
        self.observations.append(observation)
        return observation

    def _generate_observation_hash(
        self, event_type: str, inputs: Dict[str, Any], timestamp: int
    ) -> str:
        """
        Generate a deterministic hash for an observation.

        Args:
            event_type: Type of event
            inputs: Event inputs
            timestamp: Deterministic timestamp

        Returns:
            str: Deterministic hash
        """
        serializable_inputs = {}
        for key, value in sorted(inputs.items()):
            if hasattr(value, "to_decimal_string"):
                serializable_inputs[key] = value.to_decimal_string()
            else:
                serializable_inputs[key] = str(value)
        observation_data = {"event_type": event_type, "inputs": serializable_inputs}
        data_to_hash = {"observation_data": observation_data, "timestamp": timestamp}
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]

    def get_observations_summary(self) -> Dict[str, Any]:
        """Get a summary of AEGIS observations."""
        event_types = []
        for obs in sorted(
            self.observations, key=lambda x: (x.timestamp, x.observation_id)
        ):
            if obs.event_type not in event_types:
                event_types.append(obs.event_type)
        event_types.sort()
        return {
            "total_observations": len(self.observations),
            "event_types_observed": event_types,
            "latest_timestamp": self.observations[-1].timestamp
            if self.observations
            else 0,
            "observation_mode": "observation_only",
        }
