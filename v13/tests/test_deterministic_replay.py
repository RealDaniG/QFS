"""
Deterministic replay test for feed and interaction API responses
"""
import sys
import os
import hashlib
import json
from typing import List, Dict, Any


# Try different import paths
try:
    from atlas_api.gateway import AtlasAPIGateway
    from atlas_api.models import FeedRequest, InteractionRequest
    from libs.CertifiedMath import CertifiedMath, BigNum128
    from core.TokenStateBundle import TokenStateBundle
except ImportError:
    try:
        from v13.atlas_api.gateway import AtlasAPIGateway
        from v13.atlas_api.models import FeedRequest, InteractionRequest
        from v13.libs.CertifiedMath import CertifiedMath, BigNum128
        from v13.core.TokenStateBundle import TokenStateBundle
    except ImportError:
        # Direct import from current directory
        from atlas_api.gateway import AtlasAPIGateway
        from atlas_api.models import FeedRequest, InteractionRequest
        from libs.CertifiedMath import CertifiedMath, BigNum128
        from core.TokenStateBundle import TokenStateBundle


class TestDeterministicReplay:
    """Test suite for deterministic replay of feed and interaction sequences"""

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
            storage_metrics={
                "storage_bytes_stored": {},
                "storage_uptime_bucket": {},
                "storage_proofs_verified": {}
            },
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

    def _serialize_response(self, response) -> str:
        """Serialize response to a deterministic string for comparison"""
        if hasattr(response, '__dict__'):
            # Convert response object to dictionary
            response_dict = {}
            for key, value in response.__dict__.items():
                if hasattr(value, 'to_decimal_string'):
                    response_dict[key] = value.to_decimal_string()
                elif isinstance(value, list):
                    response_dict[key] = [self._serialize_response(item) for item in value]
                elif hasattr(value, '__dict__'):
                    response_dict[key] = self._serialize_response(value)
                else:
                    response_dict[key] = value
            # Sort keys for deterministic serialization
            return json.dumps(response_dict, sort_keys=True, default=str)
        else:
            return str(response)

    def _hash_responses(self, responses: List[Any]) -> str:
        """Create a hash of all responses for comparison"""
        serialized = [self._serialize_response(resp) for resp in responses]
        combined = "|".join(serialized)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def test_feed_and_interactions_deterministic_replay(self):
        """Test that a fixed sequence of feed requests and interactions produces identical results across runs"""
        # Define a fixed test scenario
        test_scenario = {
            "feed_requests": [
                {"user_id": "user_001", "limit": 3, "mode": "coherence"},
                {"user_id": "user_002", "limit": 2, "mode": "coherence"}
            ],
            "interactions": [
                {"type": "like", "user_id": "user_001", "target_id": "post_001", "content": "Great post!"},
                {"type": "comment", "user_id": "user_002", "target_id": "post_002", "content": "This is a safe, family-friendly comment."},
                {"type": "like", "user_id": "user_003", "target_id": "post_003", "content": "Buy now! Click here for free money!"},  # Spam content
            ]
        }
        
        # Run the scenario twice with fresh gateways to verify deterministic behavior
        run1_responses = self._run_scenario_with_fresh_gateway(test_scenario)
        run2_responses = self._run_scenario_with_fresh_gateway(test_scenario)
        
        # Hash the responses from both runs
        run1_hash = self._hash_responses(run1_responses)
        run2_hash = self._hash_responses(run2_responses)
        
        # Assert that both runs produce identical results
        assert run1_hash == run2_hash, f"Deterministic replay failed: run1_hash={run1_hash}, run2_hash={run2_hash}"

    def _run_scenario(self, scenario: Dict[str, Any]) -> List[Any]:
        """Run a test scenario and return all responses"""
        responses = []
        
        # Process feed requests
        for feed_req_data in scenario["feed_requests"]:
            request = FeedRequest(**feed_req_data)
            response = self.gateway.get_feed(request)
            responses.append(response)
        
        # Process interactions
        for interaction_data in scenario["interactions"]:
            interaction_type = interaction_data["type"]
            # Create a copy without the type field
            req_data = {k: v for k, v in interaction_data.items() if k != "type"}
            request = InteractionRequest(**req_data)
            response = self.gateway.post_interaction(interaction_type, request)
            responses.append(response)
            
        return responses
        
    def _run_scenario_with_fresh_gateway(self, scenario: Dict[str, Any]) -> List[Any]:
        """Run a test scenario with a fresh gateway to ensure deterministic behavior"""
        # Create a fresh gateway with the same token bundle
        fresh_gateway = AtlasAPIGateway()
        fresh_gateway.mock_token_bundle = self.token_bundle
        
        # Store reference to original gateway
        original_gateway = self.gateway
        
        # Temporarily replace gateway
        self.gateway = fresh_gateway
        
        # Run scenario
        responses = self._run_scenario(scenario)
        
        # Restore original gateway
        self.gateway = original_gateway
        
        return responses

    def test_response_structure_consistency(self):
        """Test that response structures consistently include AEGIS advisory metadata"""
        # Test feed response structure
        feed_request = FeedRequest(user_id="test_user", limit=2, mode="coherence")
        feed_response = self.gateway.get_feed(feed_request)
        
        # Verify feed posts include AEGIS advisory
        assert len(feed_response.posts) > 0
        for post in feed_response.posts:
            assert hasattr(post, 'aegis_advisory')
            assert post.aegis_advisory is not None
            assert "block_suggested" in post.aegis_advisory
            assert "severity" in post.aegis_advisory
        
        # Test interaction response structure
        interaction_request = InteractionRequest(
            user_id="test_user",
            target_id="test_post",
            content="This is a test comment."
        )
        interaction_response = self.gateway.post_interaction("comment", interaction_request)
        
        # Verify interaction response includes AEGIS advisory
        assert hasattr(interaction_response, 'aegis_advisory')
        assert interaction_response.aegis_advisory is not None
        assert "block_suggested" in interaction_response.aegis_advisory
        assert "severity" in interaction_response.aegis_advisory


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])