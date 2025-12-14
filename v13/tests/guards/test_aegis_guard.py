"""
Tests for AEGIS Guard implementation
"""
import pytest
from v13.guards.AEGISGuard import AEGISGuard, AEGISObservation
from v13.libs.CertifiedMath import CertifiedMath
from v13.core.TokenStateBundle import create_token_state_bundle, BigNum128


class TestAEGISGuard:
    """Test suite for AEGIS Guard"""

    def test_aegis_guard_initialization(self):
        """Test that AEGIS Guard initializes correctly"""
        cm = CertifiedMath()
        aegis_guard = AEGISGuard(cm)
        
        assert aegis_guard is not None
        assert aegis_guard.cm == cm
        assert hasattr(aegis_guard, 'economics_guard')
        assert aegis_guard.observations == []

    def test_observe_event_creates_observation(self):
        """Test that observing an event creates an observation record"""
        cm = CertifiedMath()
        aegis_guard = AEGISGuard(cm)
        
        # Create mock token bundle
        token_bundle = create_token_state_bundle(
            chr_state={"coherence_metric": "0.98", "c_holo_proxy": "0.99"},
            flx_state={"flux_metric": "0.15"},
            psi_sync_state={"psi_sync_metric": "0.08"},
            atr_state={"atr_metric": "0.85"},
            res_state={"resonance_metric": "0.05"},
            nod_state={"nod_metric": "0.5"},
            lambda1=BigNum128(1618033988749894848),
            lambda2=BigNum128(618033988749894848),
            c_crit=BigNum128.from_int(1),
            pqc_cid="test_pqc_cid",
            timestamp=1234567890
        )
        
        # Test inputs
        inputs = {
            "user_id": "test_user",
            "event_type": "feed_ranking",
            "score": "0.95"
        }
        
        # Observe event
        observation = aegis_guard.observe_event(
            event_type="feed_ranking",
            inputs=inputs,
            token_bundle=token_bundle,
            deterministic_timestamp=1234567890
        )
        
        # Verify observation
        assert isinstance(observation, AEGISObservation)
        assert observation.observation_id is not None
        assert len(observation.observation_id) > 0
        assert observation.timestamp == 1234567890
        assert observation.event_type == "feed_ranking"
        assert observation.inputs == inputs
        assert observation.aegis_decision == "observe"
        assert observation.safety_guard_result is not None
        assert observation.economics_guard_result is not None
        
        # Verify observation was stored
        assert len(aegis_guard.observations) == 1
        assert aegis_guard.observations[0] == observation

    def test_multiple_observations(self):
        """Test that multiple observations are handled correctly"""
        cm = CertifiedMath()
        aegis_guard = AEGISGuard(cm)
        
        # Create mock token bundle
        token_bundle = create_token_state_bundle(
            chr_state={"coherence_metric": "0.98", "c_holo_proxy": "0.99"},
            flx_state={"flux_metric": "0.15"},
            psi_sync_state={"psi_sync_metric": "0.08"},
            atr_state={"atr_metric": "0.85"},
            res_state={"resonance_metric": "0.05"},
            nod_state={"nod_metric": "0.5"},
            lambda1=BigNum128(1618033988749894848),
            lambda2=BigNum128(618033988749894848),
            c_crit=BigNum128.from_int(1),
            pqc_cid="test_pqc_cid",
            timestamp=1234567890
        )
        
        # Observe multiple events
        observation1 = aegis_guard.observe_event(
            event_type="feed_ranking",
            inputs={"event": "1"},
            token_bundle=token_bundle,
            deterministic_timestamp=1234567890
        )
        
        observation2 = aegis_guard.observe_event(
            event_type="social_interaction",
            inputs={"event": "2"},
            token_bundle=token_bundle,
            deterministic_timestamp=1234567891
        )
        
        # Verify both observations
        assert len(aegis_guard.observations) == 2
        assert aegis_guard.observations[0] == observation1
        assert aegis_guard.observations[1] == observation2
        
        # Test summary
        summary = aegis_guard.get_observations_summary()
        assert summary["total_observations"] == 2
        assert "feed_ranking" in summary["event_types_observed"]
        assert "social_interaction" in summary["event_types_observed"]
        assert summary["observation_mode"] == "observation_only"

    def test_deterministic_observations(self):
        """Test that observations are deterministic for identical inputs"""
        cm = CertifiedMath()
        
        # Create two guard instances
        guard1 = AEGISGuard(cm)
        guard2 = AEGISGuard(cm)
        
        # Create identical inputs
        token_bundle = create_token_state_bundle(
            chr_state={"coherence_metric": "0.98", "c_holo_proxy": "0.99"},
            flx_state={"flux_metric": "0.15"},
            psi_sync_state={"psi_sync_metric": "0.08"},
            atr_state={"atr_metric": "0.85"},
            res_state={"resonance_metric": "0.05"},
            nod_state={"nod_metric": "0.5"},
            lambda1=BigNum128(1618033988749894848),
            lambda2=BigNum128(618033988749894848),
            c_crit=BigNum128.from_int(1),
            pqc_cid="test_pqc_cid",
            timestamp=1234567890
        )
        
        inputs = {
            "user_id": "test_user",
            "event_type": "test_event",
            "data": "test_data"
        }
        
        # Observe identical events
        obs1 = guard1.observe_event(
            event_type="test_event",
            inputs=inputs,
            token_bundle=token_bundle,
            deterministic_timestamp=1234567890
        )
        
        obs2 = guard2.observe_event(
            event_type="test_event",
            inputs=inputs,
            token_bundle=token_bundle,
            deterministic_timestamp=1234567890
        )
        
        # Verify deterministic behavior
        assert obs1.observation_id == obs2.observation_id
        assert obs1.timestamp == obs2.timestamp
        assert obs1.event_type == obs2.event_type


if __name__ == "__main__":
    pytest.main([__file__])