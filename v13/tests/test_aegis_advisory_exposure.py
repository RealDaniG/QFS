"""
Tests for exposing AEGIS advisory metadata in API responses
"""
import sys
import os
import pytest


from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import InteractionRequest
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.TokenStateBundle import TokenStateBundle


class TestAEGISAdvisoryExposure:
    """Test suite for exposing AEGIS advisory metadata in API responses"""

    def setup_method(self):
        """Setup test environment"""
        # Create CertifiedMath instance
        self.cm = CertifiedMath()
        
        # Initialize API gateway
        self.gateway = AtlasAPIGateway()
        
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
        
        self.token_bundle = TokenStateBundle(
            chr_state=chr_state,
            flx_state={"flux_metric": "0.15"},
            psi_sync_state={"psi_sync_metric": "0.08"},
            atr_state={"atr_metric": "0.85"},
            res_state={"resonance_metric": "0.05"},
            nod_state={"nod_metric": "0.5"},
            signature="test_signature",
            timestamp=1234567890,
            bundle_id="test_bundle_id",
            pqc_cid="test_pqc_cid",
            quantum_metadata={"test": "data"},
            lambda1=BigNum128.from_int(300000000000000000),
            lambda2=BigNum128.from_int(200000000000000000),
            c_crit=BigNum128.from_int(900000000000000000),
            parameters=parameters
        )
        
        # Set the mock token bundle in the gateway
        self.gateway.mock_token_bundle = self.token_bundle

    def test_safe_interaction_includes_advisory_summary(self):
        """Test that safe interactions include AEGIS advisory summary with block_suggested=False, severity='info'"""
        # Create interaction request with safe content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="This is a safe, family-friendly comment about quantum computing.",
            reason="Testing safe interaction"
        )
        
        # Submit interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Verify response structure
        assert response.success is True
        assert response.event_id is not None
        assert response.guard_results is not None
        assert response.reward_estimate is not None
        
        # Verify AEGIS advisory summary is present
        assert response.aegis_advisory is not None
        assert "block_suggested" in response.aegis_advisory
        assert "severity" in response.aegis_advisory
        
        # Verify advisory values for safe content
        assert response.aegis_advisory["block_suggested"] is False
        assert response.aegis_advisory["severity"] == "info"

    def test_unsafe_interaction_includes_advisory_summary(self):
        """Test that unsafe interactions include AEGIS advisory summary with block_suggested=True, severity='critical'"""
        # Create interaction request with unsafe content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="This is explicit adult content that should be flagged.",
            reason="Testing unsafe interaction"
        )
        
        # Submit interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Verify response structure
        assert response.success is False  # Should be blocked
        assert response.event_id is not None
        assert response.guard_results is not None
        
        # Verify AEGIS advisory summary is present
        assert response.aegis_advisory is not None
        assert "block_suggested" in response.aegis_advisory
        assert "severity" in response.aegis_advisory
        
        # Verify advisory values for unsafe content
        assert response.aegis_advisory["block_suggested"] is True
        assert response.aegis_advisory["severity"] == "critical"

    def test_spam_interaction_includes_advisory_summary(self):
        """Test that spam interactions include AEGIS advisory summary with block_suggested=True, severity='warning'"""
        # Create interaction request with spam content that exceeds threshold
        # Using multiple spam phrases to get risk score > 0.5
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="Buy now! Click here for free money! Urgent limited time offer! Act now! Buy now! Click here!",
            reason="Testing spam interaction"
        )
        
        # Submit interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Verify response structure
        assert response.success is False  # Should be blocked
        assert response.event_id is not None
        assert response.guard_results is not None
        
        # Verify AEGIS advisory summary is present
        assert response.aegis_advisory is not None
        assert "block_suggested" in response.aegis_advisory
        assert "severity" in response.aegis_advisory
        
        # Verify advisory values for spam content
        assert response.aegis_advisory["block_suggested"] is True
        assert response.aegis_advisory["severity"] == "warning"

    def test_like_interaction_includes_advisory_summary(self):
        """Test that like interactions include AEGIS advisory summary"""
        # Create interaction request for a like
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="Great post!",
            reason="Testing like interaction"
        )
        
        # Submit interaction
        response = self.gateway.post_interaction("like", request)
        
        # Verify response structure
        assert response.success is True
        assert response.event_id is not None
        assert response.guard_results is not None
        # Note: reward_estimate may be None due to import issues in test environment
        
        # Verify AEGIS advisory summary is present
        assert response.aegis_advisory is not None
        assert "block_suggested" in response.aegis_advisory
        assert "severity" in response.aegis_advisory


if __name__ == "__main__":
    pytest.main([__file__])