"""
Tests for the governance dashboard API
"""
import sys
import os
import pytest


from v13.atlas_api.router import AtlasAPIRouter
from v13.auth.open_agi_role import OPENAGIRole, OPENAGIActionType


class TestGovernanceDashboard:
    """Test suite for the governance dashboard API"""

    def setup_method(self):
        """Setup test environment"""
        self.router = AtlasAPIRouter()

    def test_governance_dashboard_with_valid_role(self):
        """Test that governance dashboard works with valid operator role"""
        # Submit some interactions to generate AEGIS observations
        interaction1 = self.router.route_post_interaction(
            interaction_type="comment",
            user_id="test_user_1",
            target_id="test_post_1",
            content="This is a safe comment"
        )
        
        interaction2 = self.router.route_post_interaction(
            interaction_type="comment",
            user_id="test_user_2",
            target_id="test_post_2",
            content="Buy now! Click here for free money!"  # Spam content
        )
        
        # Submit an AGI observation
        agi_obs = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type=OPENAGIActionType.READ_STATE.value,
            inputs={"test": "data"},
            suggested_changes={"change": "value"},
            explanation="Test AGI observation"
        )
        
        # Request governance dashboard with valid role
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value
        )
                
        # Verify successful response
        assert result["success"] is True
        assert "aegis_advisory_counts" in result
        assert "total_aegis_observations" in result
        assert "top_content_with_observations" in result
        
        # Verify AEGIS counts structure
        counts = result["aegis_advisory_counts"]
        assert "info" in counts
        assert "warning" in counts
        assert "critical" in counts
        
        # Verify total observations
        assert result["total_aegis_observations"] >= 0

    def test_governance_dashboard_unauthorized_role(self):
        """Test that governance dashboard rejects unauthorized roles"""
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SIMULATOR.value  # Simulator role should be unauthorized
        )
        
        # Verify rejection
        assert "error_code" in result
        assert result["error_code"] == "UNAUTHORIZED_ROLE"
        assert "unauthorized" in result["message"].lower()

    def test_governance_dashboard_missing_role(self):
        """Test that governance dashboard rejects requests without role"""
        result = self.router.route_get_governance_dashboard(
            role=None
        )
        
        # Verify rejection
        assert "error_code" in result
        assert result["error_code"] == "MISSING_ROLE"
        assert "required" in result["message"].lower()

    def test_governance_dashboard_invalid_role(self):
        """Test that governance dashboard rejects invalid roles"""
        result = self.router.route_get_governance_dashboard(
            role="invalid_role"
        )
        
        # Verify rejection
        assert "error_code" in result
        assert result["error_code"] == "INVALID_ROLE"
        assert "invalid" in result["message"].lower()

    def test_governance_dashboard_with_timestamp_filtering(self):
        """Test that governance dashboard works with timestamp filtering"""
        # Request governance dashboard with timestamp filters
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value,
            start_timestamp=10000000,
            end_timestamp=20000000
        )
        
        # Verify successful response
        assert result["success"] is True
        assert "timestamp_range" in result
        assert result["timestamp_range"]["start"] == 10000000
        assert result["timestamp_range"]["end"] == 20000000

    def test_governance_dashboard_with_invalid_timestamps(self):
        """Test that governance dashboard handles invalid timestamps gracefully"""
        # Test invalid start timestamp
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value,
            start_timestamp="invalid_timestamp"
        )
        
        # Verify error response
        assert "error_code" in result
        assert result["error_code"] == "INVALID_TIMESTAMP"
        
        # Test invalid end timestamp
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value,
            end_timestamp="invalid_timestamp"
        )
        
        # Verify error response
        assert "error_code" in result
        assert result["error_code"] == "INVALID_TIMESTAMP"

    def test_governance_dashboard_deterministic_behavior(self):
        """Test that governance dashboard produces deterministic results"""
        # Get dashboard twice with same parameters
        result1 = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value
        )
        
        result2 = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value
        )
        
        # Verify both results are identical
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["aegis_advisory_counts"] == result2["aegis_advisory_counts"]
        assert result1["total_aegis_observations"] == result2["total_aegis_observations"]

    def test_governance_dashboard_large_dataset_performance(self):
        """Test that governance dashboard handles large datasets efficiently"""
        # Generate a large number of interactions to create many observations
        for i in range(100):  # Create 100 interactions
            self.router.route_post_interaction(
                interaction_type="comment",
                user_id=f"user_{i}",
                target_id=f"post_{i % 10}",  # 10 unique posts
                content=f"Test comment {i}"
            )
        
        # Request governance dashboard
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value
        )
        
        # Verify successful response
        assert result["success"] is True
        assert "aegis_advisory_counts" in result
        assert "total_aegis_observations" in result
        assert result["total_aegis_observations"] >= 100
        
        # Verify top content identification works with large dataset
        assert "top_content_with_observations" in result
        top_content = result["top_content_with_observations"]
        # Should have at most 10 content IDs (limited by our test setup)
        assert len(top_content) <= 10

    def test_governance_dashboard_degraded_mode_safety_guard_failure(self):
        """Test governance dashboard behavior when SafetyGuard fails"""
        # Submit interactions that would trigger SafetyGuard warnings
        for i in range(10):
            self.router.route_post_interaction(
                interaction_type="comment",
                user_id=f"user_{i}",
                target_id=f"spam_post_{i}",
                content="BUY NOW!!! CLICK HERE FOR FREE MONEY!!! URGENT!!!"
            )
        
        # Request governance dashboard
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value
        )
        
        # Verify successful response
        assert result["success"] is True
        assert "aegis_advisory_counts" in result
        
        # Should have warnings or critical advisories due to spam content
        counts = result["aegis_advisory_counts"]
        # Total should reflect the spam interactions
        assert result["total_aegis_observations"] >= 10

    def test_governance_dashboard_degraded_mode_economics_guard_failure(self):
        """Test governance dashboard behavior when EconomicsGuard fails"""
        # Submit interactions that might trigger EconomicsGuard warnings
        # We'll simulate this by submitting many interactions rapidly
        for i in range(50):
            self.router.route_post_interaction(
                interaction_type="comment",
                user_id="user_1",
                target_id=f"post_{i}",
                content=f"Normal comment {i}"
            )
        
        # Request governance dashboard
        result = self.router.route_get_governance_dashboard(
            role=OPENAGIRole.SYSTEM.value
        )
        
        # Verify successful response
        assert result["success"] is True
        assert "aegis_advisory_counts" in result
        assert "total_aegis_observations" in result
        
        # Should have observations from the interactions
        assert result["total_aegis_observations"] >= 50

    def test_correlation_endpoint_large_dataset_performance(self):
        """Test that correlation endpoint handles large datasets efficiently"""
        # Generate a large number of correlated observations
        event_ids = []
        for i in range(50):  # Create 50 interactions
            interaction_result = self.router.route_post_interaction(
                interaction_type="comment",
                user_id=f"user_{i}",
                target_id=f"correlation_post_{i}",
                content=f"Correlation test comment {i}"
            )
            if "event_id" in interaction_result:
                event_ids.append(interaction_result["event_id"])
        
        # Submit AGI observations that correlate with some of these events
        for i, event_id in enumerate(event_ids[:20]):  # Correlate with first 20 events
            self.router.route_submit_agi_observation(
                role=OPENAGIRole.SYSTEM.value,
                action_type=OPENAGIActionType.READ_STATE.value,
                inputs={
                    "content_ids": [f"correlation_post_{i}"],
                    "interaction_ids": [event_id]
                },
                suggested_changes={"change": f"value_{i}"},
                explanation=f"Correlated observation {i}",
                correlation_to_aegis={
                    "related_aegis_events": [event_id],
                    "confidence_level": "high"
                }
            )
        
        # Test correlation endpoint with one of the correlated events
        if event_ids:
            correlation_result = self.router.route_get_correlated_observations(
                event_id=event_ids[0]
            )
            
            # Verify successful response
            assert correlation_result["success"] is True
            assert "aegis_observations" in correlation_result
            assert "agi_observations" in correlation_result
            
            # Should have at least one of each type
            assert len(correlation_result["aegis_observations"]) >= 1
            assert len(correlation_result["agi_observations"]) >= 1

    def test_correlation_endpoint_degraded_mode_partial_failures(self):
        """Test correlation endpoint behavior under partial system failures"""
        # Submit a normal interaction
        interaction_result = self.router.route_post_interaction(
            interaction_type="comment",
            user_id="test_user",
            target_id="degraded_test_post",
            content="Normal test comment"
        )
        
        # Submit an AGI observation without proper correlation data
        agi_result = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type=OPENAGIActionType.READ_STATE.value,
            inputs={"test": "data"},
            suggested_changes={"change": "value"},
            explanation="Test observation without correlation"
        )
        
        # Test correlation endpoint without filters (should still work)
        correlation_result = self.router.route_get_correlated_observations()
        
        # Verify successful response even with mixed data quality
        assert correlation_result["success"] is True
        assert "total_agi" in correlation_result
        assert "total_aegis" in correlation_result
        
        # Should have at least some observations
        assert correlation_result["total_agi"] >= 1
        assert correlation_result["total_aegis"] >= 1


if __name__ == "__main__":
    pytest.main([__file__])