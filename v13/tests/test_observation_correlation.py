"""
Tests for observation correlation between AEGIS and AGI observations
"""
import pytest
from v13.atlas_api.router import AtlasAPIRouter
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.auth.open_agi_role import OPENAGIRole, OPENAGIActionType

class TestObservationCorrelation:
    """Test suite for observation correlation between AEGIS and AGI observations"""

    def setup_method(self):
        """Setup test environment"""
        self.router = AtlasAPIRouter()
        self.gateway = AtlasAPIGateway()

    def test_correlate_agi_with_aegis_observations(self):
        """Test that AGI observations can be correlated with AEGIS observations"""
        interaction_result = self.router.route_post_interaction(interaction_type='comment', user_id='test_user', target_id='test_post', content='This is a test comment with potential issues')
        assert 'event_id' in interaction_result
        event_id = interaction_result['event_id']
        agi_result = self.router.route_submit_agi_observation(role=OPENAGIRole.SYSTEM.value, action_type=OPENAGIActionType.READ_STATE.value, inputs={'content_ids': ['test_post'], 'interaction_ids': [event_id]}, suggested_changes={'threshold_adjustment': {'safety_risk_threshold': '0.85'}}, explanation='Detected pattern requiring adjusted thresholds', correlation_to_aegis={'related_aegis_events': [event_id], 'confidence_level': 'high'})
        assert agi_result['success'] is True
        assert 'observation_id' in agi_result
        correlation_result = self.router.route_get_correlated_observations(event_id=event_id)
        assert correlation_result['success'] is True
        assert correlation_result['total_aegis'] >= 1
        assert correlation_result['total_agi'] >= 1
        aegis_obs = correlation_result['aegis_observations']
        agi_obs = correlation_result['agi_observations']
        assert len(aegis_obs) >= 1
        assert len(agi_obs) >= 1
        found_agi_with_correlation = False
        for obs in sorted(agi_obs):
            if 'observation_data' in obs and 'correlated_aegis_observations' in obs['observation_data']:
                if event_id in obs['observation_data']['correlated_aegis_observations']:
                    found_agi_with_correlation = True
                    break
        assert found_agi_with_correlation is True

    def test_get_all_observations_without_filter(self):
        """Test that we can get all observations without filtering"""
        agi_result = self.router.route_submit_agi_observation(role=OPENAGIRole.SYSTEM.value, action_type=OPENAGIActionType.READ_STATE.value, inputs={'test': 'data'}, suggested_changes={'change': 'value'}, explanation='Test observation')
        assert agi_result['success'] is True
        correlation_result = self.router.route_get_correlated_observations()
        assert correlation_result['success'] is True
        assert correlation_result['total_agi'] >= 1

    def test_correlation_with_content_id(self):
        """Test correlation using content ID"""
        agi_result = self.router.route_submit_agi_observation(role=OPENAGIRole.SYSTEM.value, action_type=OPENAGIActionType.READ_STATE.value, inputs={'content_ids': ['content_123']}, suggested_changes={'change': 'value'}, explanation='Test observation', correlation_to_aegis={'related_content': ['content_123'], 'confidence_level': 'medium'})
        assert agi_result['success'] is True
        correlation_result = self.router.route_get_correlated_observations(content_id='content_123')
        assert correlation_result['success'] is True
if __name__ == '__main__':
    pytest.main([__file__])