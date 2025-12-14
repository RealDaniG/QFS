"""
Tests for token state service extension point
"""
import sys
import os
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
        
        # Create a distinct token bundle with unique values
        chr_state = {
            "coherence_metric": "0.95",  # Different from mock
            "c_holo_proxy": "0.97",      # Different from mock
            "resonance_metric": "0.10",  # Different from mock
            "flux_metric": "0.20",       # Different from mock
            "psi_sync_metric": "0.15",   # Different from mock
            "atr_metric": "0.90"         # Different from mock
        }
        
        parameters = {
            "beta_penalty": BigNum128.from_int(200000000),  # Different from mock
            "phi": BigNum128.from_int(1618033988749894848)
        }
        
        return TokenStateBundle(
            chr_state=chr_state,
            flx_state={"flux_metric": "0.20"},
            psi_sync_state={"psi_sync_metric": "0.15"},
            atr_state={"atr_metric": "0.90"},
            res_state={"resonance_metric": "0.10"},
            nod_state={"nod_metric": "0.6"},  # Different from mock
            signature="fake_signature",
            timestamp=1234567890,
            bundle_id=f"fake_bundle_{user_id}",
            pqc_cid="fake_pqc_cid",
            quantum_metadata={"source": "fake_token_service"},
            lambda1=BigNum128.from_int(400000000000000000),  # Different from mock
            lambda2=BigNum128.from_int(300000000000000000),  # Different from mock
            c_crit=BigNum128.from_int(800000000000000000),   # Different from mock
            parameters=parameters
        )


class TestTokenStateExtension:
    """Test suite for token state service extension point"""

    def test_token_state_service_extension(self):
        """Test that setting a token state service changes behavior"""
        gateway = AtlasAPIGateway()
        
        # Test with mock token bundle (default behavior)
        mock_bundle = gateway._get_user_token_bundle("test_user")
        assert mock_bundle.nod_state["nod_metric"] == "0.5"  # From mock
        
        # Set up fake token state service
        fake_service = FakeTokenStateService()
        gateway.set_token_state_service(fake_service)
        
        # Test with real token service
        real_bundle = gateway._get_user_token_bundle("test_user")
        
        # Verify the service was called
        assert fake_service.call_count == 1
        assert fake_service.last_user_id == "test_user"
        
        # Verify we got a different bundle
        assert real_bundle.nod_state["nod_metric"] == "0.6"  # From fake service
        assert real_bundle.bundle_id == "fake_bundle_test_user"
        
        # Test that interaction uses the real bundle
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_post",
            content="This is a safe comment."
        )
        
        response = gateway.post_interaction("comment", request)
        
        # Verify response was successful
        assert response.success is not None
        assert response.event_id is not None

    def test_token_state_service_fallback(self):
        """Test that gateway falls back to mock when service fails"""
        gateway = AtlasAPIGateway()
        
        # Create a fake service that always fails
        class FailingTokenStateService:
            def get_bundle_for_user(self, user_id):
                raise Exception("Service unavailable")
        
        failing_service = FailingTokenStateService()
        gateway.set_token_state_service(failing_service)
        
        # Should fall back to mock bundle
        bundle = gateway._get_user_token_bundle("test_user")
        assert bundle.nod_state["nod_metric"] == "0.5"  # From mock


if __name__ == "__main__":
    pytest.main([__file__])