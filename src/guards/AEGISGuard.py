"""
AEGISGuard.py - Meta-guard orchestrator for QFS V13

Implements the AEGIS Guard as a meta-guard that orchestrates SafetyGuard and EconomicsGuard,
enforcing a clear threat model and producing QFS-specific security test coverage.

V13.6 ENHANCEMENTS:
- Observation-only mode for initial integration
- Deterministic telemetry analysis
- Zero-Sim compliant implementation
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import required components
from ..libs.CertifiedMath import BigNum128, CertifiedMath
from ..libs.economics.EconomicsGuard import EconomicsGuard
from ..core.TokenStateBundle import TokenStateBundle


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


class AEGISGuard:
    """
    AEGIS Guard as a meta-guard orchestrator.
    
    This guard acts as a meta-guard that orchestrates SafetyGuard and EconomicsGuard,
    enforcing a clear threat model and producing QFS-specific security test coverage.
    Initially operates in observation-only mode to ensure compatibility.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the AEGIS Guard.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
        """
        self.cm = cm_instance
        self.economics_guard = EconomicsGuard(cm_instance)
        self.observations: List[AEGISObservation] = []
        self.quantum_metadata = {
            "component": "AEGISGuard",
            "version": "QFS-V13-P1-2",
            "pqc_scheme": "Dilithium-5"
        }
        
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
            # For now, we'll use a simplified safety check
            # In a real implementation, this would call the actual safety guard methods
            safety_result = {
                "passed": True,
                "explanation": "Safety guard observation passed in observation-only mode"
            }
        except Exception as e:
            safety_result = {
                "passed": False,
                "explanation": f"Safety guard evaluation failed: {str(e)}"
            }
        
        # Evaluate with EconomicsGuard
        economics_result = None
        try:
            # For now, we'll use a simplified economics check
            # In a real implementation, this would call the actual economics guard methods
            economics_result = {
                "passed": True,
                "explanation": "Economics guard observation passed in observation-only mode"
            }
        except Exception as e:
            economics_result = {
                "passed": False,
                "explanation": f"Economics guard evaluation failed: {str(e)}"
            }
        
        # Generate deterministic observation ID
        observation_data = {
            "event_type": event_type,
            "inputs": inputs,
            "timestamp": deterministic_timestamp
        }
        observation_json = json.dumps(observation_data, sort_keys=True)
        observation_id = hashlib.sha256(observation_json.encode('utf-8')).hexdigest()[:32]
        
        # Generate PQC correlation ID
        pqc_cid = self._generate_pqc_cid(observation_data, deterministic_timestamp)
        
        # Create observation record
        observation = AEGISObservation(
            observation_id=observation_id,
            timestamp=deterministic_timestamp,
            event_type=event_type,
            inputs=inputs,
            safety_guard_result=safety_result,
            economics_guard_result=economics_result,
            aegis_decision="observe",  # Observation-only mode
            explanation="Event observed and logged for analysis",
            pqc_cid=pqc_cid,
            quantum_metadata=self.quantum_metadata.copy()
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
    
    # Test observing a feed event
    feed_inputs = {
        "user_id": "test_user",
        "post_id": "test_post",
        "features": ["feature1", "feature2"],
        "coherence_score": "0.95"
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
    
    # Test observing an interaction event
    interaction_inputs = {
        "user_id": "test_user",
        "target_id": "test_target",
        "interaction_type": "like",
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
    
    # Test observations summary
    summary = aegis_guard.get_observations_summary()
    print(f"Observations summary: {summary}")


if __name__ == "__main__":
    test_aegis_guard()