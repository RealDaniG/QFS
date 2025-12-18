"""
Tests for token state service extension point
"""
import pytest
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import InteractionRequest
from v13.core.TokenStateBundle import TokenStateBundle
from v13.libs.CertifiedMath import BigNum128

class FakeTokenStateService:
    """Fake token state service for testing"""

    def __init__(self):
        self.call_count = 0
        self.last_user_id = None

    def get_bundle_for_user(self, user_id):
        """Return a distinct token bundle for testing"""
        self.call_count += 1
        self.last_user_id = user_id
        chr_state = {'coherence_metric': '0.95', 'c_holo_proxy': '0.97', 'resonance_metric': '0.10', 'flux_metric': '0.20', 'psi_sync_metric': '0.15', 'atr_metric': '0.90'}
        parameters = {'beta_penalty': BigNum128.from_int(200000000), 'phi': BigNum128.from_int(1618033988749894848)}
        return TokenStateBundle(chr_state=chr_state, flx_state={'flux_metric': '0.20'}, psi_sync_state={'psi_sync_metric': '0.15'}, atr_state={'atr_metric': '0.90'}, res_state={'resonance_metric': '0.10'}, nod_state={'nod_metric': '0.6'}, signature='fake_signature', timestamp=1234567890, bundle_id=f'fake_bundle_{user_id}', pqc_cid='fake_pqc_cid', quantum_metadata={'source': 'fake_token_service'}, lambda1=BigNum128.from_int(400000000000000000), lambda2=BigNum128.from_int(300000000000000000), c_crit=BigNum128.from_int(800000000000000000), parameters=parameters)

class TestTokenStateExtension:
    """Test suite for token state service extension point"""

    def test_token_state_service_extension(self):
        """Test that setting a token state service changes behavior"""
        gateway = AtlasAPIGateway()
        mock_bundle = gateway._get_user_token_bundle('test_user')
        assert mock_bundle.nod_state['nod_metric'] == '0.5'
        fake_service = FakeTokenStateService()
        gateway.set_token_state_service(fake_service)
        real_bundle = gateway._get_user_token_bundle('test_user')
        assert fake_service.call_count == 1
        assert fake_service.last_user_id == 'test_user'
        assert real_bundle.nod_state['nod_metric'] == '0.6'
        assert real_bundle.bundle_id == 'fake_bundle_test_user'
        request = InteractionRequest(user_id='test_user', target_id='test_post', content='This is a safe comment.')
        response = gateway.post_interaction('comment', request)
        assert response.success is not None
        assert response.event_id is not None

    def test_token_state_service_fallback(self):
        """Test that gateway falls back to mock when service fails"""
        gateway = AtlasAPIGateway()

        class FailingTokenStateService:

            def get_bundle_for_user(self, user_id):
                raise Exception('Service unavailable')
        failing_service = FailingTokenStateService()
        gateway.set_token_state_service(failing_service)
        bundle = gateway._get_user_token_bundle('test_user')
        assert bundle.nod_state['nod_metric'] == '0.5'
if __name__ == '__main__':
    pytest.main([__file__])
