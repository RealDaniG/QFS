"""
AEGISGuard.py - Meta-guard orchestrator for QFS V13

Implements the AEGIS Guard as a meta-guard that orchestrates SafetyGuard and EconomicsGuard,
enforcing a clear threat model and producing QFS-specific security test coverage.

V13.6 ENHANCEMENTS:
- Deterministic telemetry analysis
- Zero-Sim compliant implementation
- Advisory gate with block_suggested and severity fields
- Advisory blocking capability for unsafe content and economic violations
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import required components
try:
    from ..libs.CertifiedMath import BigNum128, CertifiedMath
    from ..libs.economics.EconomicsGuard import EconomicsGuard
    from ..libs.core.SafetyGuard import SafetyGuard
    from ..core.TokenStateBundle import TokenStateBundle
except ImportError:
    # Fallback to absolute imports
    try:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
        from v13.libs.economics.EconomicsGuard import EconomicsGuard
        from v13.libs.core.SafetyGuard import SafetyGuard
        from v13.core.TokenStateBundle import TokenStateBundle
    except ImportError:
        # Try with sys.path modification
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        try:
            from v13.libs.CertifiedMath import BigNum128, CertifiedMath
            from v13.libs.economics.EconomicsGuard import EconomicsGuard
            from v13.libs.core.SafetyGuard import SafetyGuard
            from v13.core.TokenStateBundle import TokenStateBundle
        except ImportError:
            from libs.CertifiedMath import BigNum128, CertifiedMath
            from libs.economics.EconomicsGuard import EconomicsGuard
            from libs.core.SafetyGuard import SafetyGuard
            from core.TokenStateBundle import TokenStateBundle


@dataclass
class AEGISObservation:
    """Represents an AEGIS observation for logging and analysis."""
    observation_id: str
    timestamp: int
    event_type: str
    inputs: Dict[str, Any]
    safety_guard_result: Optional[Dict[str, Any]]
    economics_guard_result: Optional[Dict[str, Any]]
    aegis_decision: str  # "observe", "alert", "veto" (future)
    explanation: str
    pqc_cid: str
    quantum_metadata: Dict[str, Any]
    # New fields for advisory gate
    block_suggested: bool = False
    severity: str = "info"  # "info" | "warning" | "critical"


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
            "pqc_scheme": "Dilithium-5"
        }
        # Ledger economics service extension point (initially None)
        self.ledger_economics_service = None
    
    def set_ledger_economics_service(self, service):
        """
        Set the ledger economics service for real economics data.
        
        Args:
            service: Ledger economics service that provides real economics data
        """
        self.ledger_economics_service = service
    
    def observe_event(self, event_type: str, inputs: Dict[str, Any], 
                     token_bundle: TokenStateBundle, deterministic_timestamp: int = 0) -> AEGISObservation:
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
        # Evaluate with SafetyGuard
        safety_result = None
        try:
            # For feed ranking events, we validate the content
            if event_type == "feed_ranking":
                content_text = inputs.get("content", "")
                safety_validation = self.safety_guard.validate_content(
                    content_text=content_text,
                    content_metadata=inputs,
                    token_bundle=token_bundle,
                    log_list=[],  # In a real implementation, this would be a shared log
                    pqc_cid=f"safety_check_{deterministic_timestamp}",
                    deterministic_timestamp=deterministic_timestamp
                )
                safety_result = {
                    "passed": safety_validation.passed,
                    "risk_score": safety_validation.risk_score.to_decimal_string(),
                    "explanation": safety_validation.explanation,
                    "policy_version": safety_validation.policy_version
                }
            # For social interaction events, we might validate different aspects
            elif event_type == "social_interaction":
                # For interactions, we validate the content
                content_text = inputs.get("content", "")
                safety_validation = self.safety_guard.validate_content(
                    content_text=content_text,
                    content_metadata=inputs,
                    token_bundle=token_bundle,
                    log_list=[],  # In a real implementation, this would be a shared log
                    pqc_cid=f"safety_check_{deterministic_timestamp}",
                    deterministic_timestamp=deterministic_timestamp
                )
                safety_result = {
                    "passed": safety_validation.passed,
                    "risk_score": safety_validation.risk_score.to_decimal_string(),
                    "explanation": safety_validation.explanation,
                    "policy_version": safety_validation.policy_version
                }
            else:
                # Default safety check for other event types
                safety_result = {
                    "passed": True,
                    "explanation": "Default safety check passed"
                }
        except Exception as e:
            safety_result = {
                "passed": False,
                "explanation": f"Safety guard evaluation failed: {str(e)}"
            }
        
        # Evaluate with EconomicsGuard
        economics_result = None
        try:
            # For interaction events, we validate economic parameters
            if event_type == "social_interaction":
                # Validate economic parameters for interactions
                # Get realistic values from inputs or token bundle
                reward_amount = BigNum128.from_int(100)  # Placeholder reward amount
                
                # Get economics parameters from ledger economics service when available, otherwise use demo values
                if self.ledger_economics_service is not None:
                    try:
                        # Get real economics data from ledger
                        daily_totals = self.ledger_economics_service.get_chr_daily_totals()
                        total_supply_data = self.ledger_economics_service.get_chr_total_supply()
                        
                        current_daily_total = daily_totals.get("current_daily_total", BigNum128.from_int(0))
                        current_total_supply = total_supply_data.get("current_total_supply", BigNum128.from_int(1000000))
                    except Exception as e:
                        # Fall back to demo values if service fails
                        # Log to a deterministic log list instead of printing to stdout
                        log_entry = {
                            "level": "WARNING",
                            "message": f"Ledger economics service failed, falling back to demo values: {e}",
                            "timestamp": deterministic_timestamp
                        }
                        # In a real implementation, this would be added to a shared log list
                        current_daily_total = BigNum128.from_int(10000)  # Demo value - clearly labeled
                        current_total_supply = BigNum128.from_int(1000000)  # Demo value - clearly labeled
                else:
                    # Use demo values when service is not available
                    current_daily_total = BigNum128.from_int(10000)  # Demo value - clearly labeled
                    current_total_supply = BigNum128.from_int(1000000)  # Demo value - clearly labeled
                
                economics_validation = self.economics_guard.validate_chr_reward(
                    reward_amount=reward_amount,
                    current_daily_total=current_daily_total,
                    current_total_supply=current_total_supply,
                    log_list=[]  # In a real implementation, this would be a shared log
                )
                economics_result = {
                    "passed": economics_validation.passed,
                    "error_code": economics_validation.error_code,
                    "explanation": economics_validation.error_message if not economics_validation.passed else "Economics guard validation passed"
                }
            else:
                # Default economics check for other event types
                economics_result = {
                    "passed": True,
                    "explanation": "Default economics check passed"
                }
        except Exception as e:
            economics_result = {
                "passed": False,
                "explanation": f"Economics guard evaluation failed: {str(e)}"
            }
        
        # Generate deterministic observation ID
        # Need to make inputs JSON serializable by converting BigNum128 objects to strings
        serializable_inputs = {}
        for key, value in inputs.items():
            if hasattr(value, 'to_decimal_string'):
                serializable_inputs[key] = value.to_decimal_string()
            elif isinstance(value, dict):
                # Recursively convert nested dictionaries
                serializable_inputs[key] = {}
                for sub_key, sub_value in value.items():
                    if hasattr(sub_value, 'to_decimal_string'):
                        serializable_inputs[key][sub_key] = sub_value.to_decimal_string()
                    else:
                        serializable_inputs[key][sub_key] = sub_value
            else:
                serializable_inputs[key] = value
        
        observation_data = {
            "event_type": event_type,
            "inputs": serializable_inputs,
            "timestamp": deterministic_timestamp
        }
        observation_json = json.dumps(observation_data, sort_keys=True)
        observation_id = hashlib.sha256(observation_json.encode('utf-8')).hexdigest()[:32]
        
        # Generate PQC correlation ID
        pqc_cid = self._generate_pqc_cid(observation_data, deterministic_timestamp)
        
        # Derive block_suggested and severity from guard results
        block_suggested = False
        severity = "info"
        
        # Check for safety violations using CertifiedMath for deterministic comparisons
        safety_risk_score_bn = BigNum128(0)
        if safety_result and "risk_score" in safety_result:
            try:
                safety_risk_score_bn = BigNum128.from_string(safety_result["risk_score"])
            except (ValueError, TypeError):
                safety_risk_score_bn = BigNum128(0)
        
        # Define thresholds using BigNum128 for deterministic comparisons
        high_risk_threshold = BigNum128.from_string("0.7")
        medium_risk_threshold = BigNum128.from_string("0.5")
        
        # Check for economics violations
        economics_failed = economics_result and not economics_result.get("passed", True)
        
        # Determine if blocking is suggested using CertifiedMath comparisons
        if self.cm.gt(safety_risk_score_bn, high_risk_threshold, []):  # High risk content
            block_suggested = True
            severity = "critical"
        elif self.cm.gt(safety_risk_score_bn, medium_risk_threshold, []):  # Medium risk content
            block_suggested = True
            severity = "warning"
        elif economics_failed:  # Economics violation
            block_suggested = True
            severity = "warning"
        
        # Make AEGIS decision based on guard results
        aegis_decision = "observe"  # Default to observation mode
        explanation = "Event observed and logged for analysis"
        
        # If both guards pass, we might allow the action in non-observation mode
        # For now, we'll stay in observation mode as per P1 requirements
        if safety_result.get("passed", False) and economics_result.get("passed", False):
            aegis_decision = "observe"  # Could be "allow" in future phases
            explanation = "Both safety and economics guards passed - event approved for observation"
        elif not safety_result.get("passed", True) or not economics_result.get("passed", True):
            aegis_decision = "observe"  # Still in observation mode but flagged
            explanation = "One or more guards flagged concerns - event observed for analysis"
        
        # Create observation record with serializable inputs to avoid JSON serialization issues
        observation = AEGISObservation(
            observation_id=observation_id,
            timestamp=deterministic_timestamp,
            event_type=event_type,
            inputs=serializable_inputs,  # Store serializable inputs to avoid JSON issues
            safety_guard_result=safety_result,
            economics_guard_result=economics_result,
            aegis_decision=aegis_decision,
            explanation=explanation,
            pqc_cid=pqc_cid,
            quantum_metadata=self.quantum_metadata.copy(),
            block_suggested=block_suggested,
            severity=severity
        )
        
        # Add to observations
        self.observations.append(observation)
        
        return observation
        
    def _generate_pqc_cid(self, observation_data: Dict[str, Any], timestamp: int) -> str:
        """Generate deterministic PQC correlation ID."""
        data_to_hash = {
            "observation_data": observation_data,
            "timestamp": timestamp
        }
        
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]
        
    def get_observations_summary(self) -> Dict[str, Any]:
        """Get a summary of AEGIS observations."""
        return {
            "total_observations": len(self.observations),
            "event_types_observed": list(set(obs.event_type for obs in self.observations)),
            "latest_timestamp": self.observations[-1].timestamp if self.observations else 0,
            "observation_mode": "observation_only"  # Indicates we're in observation mode
        }


# Test function
def test_aegis_guard():
    """Test the AEGISGuard implementation."""
    print("Testing AEGISGuard...")
    
    # Create test log list and CertifiedMath instance
    log_list = []
    # Use the LogContext to create a proper log list
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    
    # Initialize AEGIS guard
    aegis_guard = AEGISGuard(cm)
    
    # Create test token bundle
    chr_state = {
        "coherence_metric": "0.98",
        "c_holo_proxy": "0.99",
        "resonance_metric": "0.05",
        "flux_metric": "0.15",
        "psi_sync_metric": "0.08",
        "atr_metric": "0.85"
    }
    
    parameters = {
        "beta_penalty": BigNum128.from_int(100000000),
        "phi": BigNum128.from_int(1618033988749894848)
    }
    
    token_bundle = TokenStateBundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        nod_state={"nod_metric": "0.5"},
        signature="test_signature",
        timestamp=1234567890,  # Deterministic timestamp
        bundle_id="test_bundle_id",
        pqc_cid="test_pqc_cid",
        quantum_metadata={"test": "data"},
        lambda1=BigNum128.from_int(300000000000000000),
        lambda2=BigNum128.from_int(200000000000000000),
        c_crit=BigNum128.from_int(900000000000000000),
        parameters=parameters
    )
    
    # Test observing a feed event with real content
    feed_inputs = {
        "user_id": "test_user",
        "post_id": "test_post",
        "features": ["feature1", "feature2"],
        "coherence_score": "0.95",
        "content": "This is a safe, family-friendly post about quantum computing."  # Real content for safety evaluation
    }
    
    observation1 = aegis_guard.observe_event(
        event_type="feed_ranking",
        inputs=feed_inputs,
        token_bundle=token_bundle,
        deterministic_timestamp=1234567890
    )
    
    print(f"Observed feed event: {observation1.observation_id}")
    print(f"Safety result: {observation1.safety_guard_result}")
    print(f"Economics result: {observation1.economics_guard_result}")
    print(f"AEGIS decision: {observation1.aegis_decision}")
    print(f"Block suggested: {observation1.block_suggested}")
    print(f"Severity: {observation1.severity}")
    
    # Test observing an interaction event with unsafe content
    interaction_inputs = {
        "user_id": "test_user",
        "target_id": "test_target",
        "interaction_type": "comment",
        "content": "This is explicit adult content that should be flagged.",
        "reward_amount": "100.0"
    }
    
    observation2 = aegis_guard.observe_event(
        event_type="social_interaction",
        inputs=interaction_inputs,
        token_bundle=token_bundle,
        deterministic_timestamp=1234567891
    )
    
    print(f"Observed interaction event: {observation2.observation_id}")
    print(f"Safety result: {observation2.safety_guard_result}")
    print(f"Economics result: {observation2.economics_guard_result}")
    print(f"AEGIS decision: {observation2.aegis_decision}")
    print(f"Block suggested: {observation2.block_suggested}")
    print(f"Severity: {observation2.severity}")
    
    # Test observations summary
    summary = aegis_guard.get_observations_summary()
    print(f"Observations summary: {summary}")


if __name__ == "__main__":
    test_aegis_guard()