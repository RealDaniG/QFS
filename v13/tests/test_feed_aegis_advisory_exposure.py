"""
Tests for exposing AEGIS advisory metadata in feed API responses
"""
import pytest
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import FeedRequest
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.TokenStateBundle import TokenStateBundle

class TestFeedAEGISAdvisoryExposure:
    """Test suite for exposing AEGIS advisory metadata in feed API responses"""

    def setup_method(self):
        """Setup test environment"""
        self.cm = CertifiedMath()
        self.gateway = AtlasAPIGateway()
        chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99', 'resonance_metric': '0.05', 'flux_metric': '0.15', 'psi_sync_metric': '0.08', 'atr_metric': '0.85'}
        parameters = {'beta_penalty': BigNum128.from_int(100000000), 'phi': BigNum128.from_int(1618033988749894848)}
        self.token_bundle = TokenStateBundle(chr_state=chr_state, flx_state={'flux_metric': '0.15'}, psi_sync_state={'psi_sync_metric': '0.08'}, atr_state={'atr_metric': '0.85'}, res_state={'resonance_metric': '0.05'}, nod_state={'nod_metric': '0.5'}, signature='test_signature', timestamp=1234567890, bundle_id='test_bundle_id', pqc_cid='test_pqc_cid', quantum_metadata={'test': 'data'}, lambda1=BigNum128.from_int(300000000000000000), lambda2=BigNum128.from_int(200000000000000000), c_crit=BigNum128.from_int(900000000000000000), parameters=parameters)
        self.gateway.mock_token_bundle = self.token_bundle

    def test_feed_items_include_advisory_summary(self):
        """Test that feed items include AEGIS advisory summary"""
        request = FeedRequest(user_id='test_user', limit=5, mode='coherence')
        response = self.gateway.get_feed(request)
        assert response.posts is not None
        assert len(response.posts) > 0
        for post in response.posts:
            assert post.aegis_advisory is not None
            assert 'block_suggested' in post.aegis_advisory
            assert 'severity' in post.aegis_advisory
            assert isinstance(post.aegis_advisory['block_suggested'], bool)
            assert post.aegis_advisory['severity'] in ['info', 'warning', 'critical']

    def test_feed_with_mixed_content_advisory_summaries(self):
        """Test that feed with mixed content types produces appropriate advisory summaries"""
        request = FeedRequest(user_id='test_user', limit=5, mode='coherence')
        response = self.gateway.get_feed(request)
        assert response.posts is not None
        assert len(response.posts) > 0
        has_info = False
        has_warning = False
        has_critical = False
        for post in response.posts:
            assert post.aegis_advisory is not None
            severity = post.aegis_advisory['severity']
            if severity == 'info':
                has_info = True
            elif severity == 'warning':
                has_warning = True
            elif severity == 'critical':
                has_critical = True
        assert has_info is True
if __name__ == '__main__':
    pytest.main([__file__])