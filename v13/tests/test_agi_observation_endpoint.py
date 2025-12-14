"""
Tests for the AGI observation/recommendation endpoint
"""
import sys
import os
import pytest


from v13.atlas_api.router import AtlasAPIRouter
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.auth.open_agi_role import OPENAGIRole, OPENAGIActionType


class TestAGIObservationEndpoint:
    """Test suite for the AGI observation/recommendation endpoint"""

    def setup_method(self):
        """Setup test environment"""
        self.router = AtlasAPIRouter()
        self.gateway = AtlasAPIGateway()

    def test_valid_agi_observation_submission(self):
        """Test that valid AGI observation is accepted and creates ledger entry"""
        # Submit valid AGI observation
        result = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type=OPENAGIActionType.READ_STATE.value,
            inputs={
                "content_ids": ["cid_001", "cid_002"],
                "interaction_ids": ["int_001"]
            },
            suggested_changes={
                "threshold_adjustment": {
                    "safety_risk_threshold": "0.85"
                }
            },
            explanation="Detected pattern of borderline content requiring adjusted thresholds",
            correlation_to_aegis={
                "related_aegis_events": ["aegis_001", "aegis_002"],
                "confidence_level": "high"
            }
        )
        
        # Verify successful response
        assert result["success"] is True
        assert "observation_id" in result
        assert "ledger_entry_id" in result
        assert len(result["observation_id"]) == 32  # SHA256 truncated to 32 chars
        
        # Verify ledger entry was created using router's gateway
        ledger_entries = self.router.gateway.coherence_ledger.ledger_entries
        assert len(ledger_entries) > 0
        
        # Check that the latest entry contains AGI observation data
        latest_entry = ledger_entries[-1]
        assert "agi_observation" in latest_entry.data.get("hsmf_metrics", {})
        
        agi_data = latest_entry.data["hsmf_metrics"]["agi_observation"]
        assert agi_data["role"] == OPENAGIRole.SYSTEM.value
        assert agi_data["action_type"] == OPENAGIActionType.READ_STATE.value
        assert "correlation_to_aegis" in agi_data

    def test_invalid_role_rejected(self):
        """Test that invalid role is properly rejected"""
        result = self.router.route_submit_agi_observation(
            role="invalid_role",
            action_type=OPENAGIActionType.READ_STATE.value,
            inputs={"test": "data"},
            suggested_changes={"change": "value"},
            explanation="Test explanation"
        )
        
        # Verify rejection
        assert result["success"] is False
        assert result["error_code"] == "INVALID_ROLE_OR_ACTION"
        assert "not recognized" in result["details"]

    def test_invalid_action_type_rejected(self):
        """Test that invalid action type is properly rejected"""
        result = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type="invalid_action",
            inputs={"test": "data"},
            suggested_changes={"change": "value"},
            explanation="Test explanation"
        )
        
        # Verify rejection
        assert result["success"] is False
        assert result["error_code"] == "INVALID_ROLE_OR_ACTION"
        assert "not recognized" in result["details"]

    def test_unauthorized_role_action_combination(self):
        """Test that unauthorized role/action combinations are rejected"""
        # Try to submit a proposal action with SYSTEM role (should be unauthorized)
        result = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type=OPENAGIActionType.PROPOSE_INTERVENTION.value,
            inputs={"test": "data"},
            suggested_changes={"change": "value"},
            explanation="Test explanation"
        )
        
        # Verify rejection
        assert result["success"] is False
        assert result["error_code"] == "UNAUTHORIZED"
        assert "not authorized" in result["message"]

    def test_missing_required_fields(self):
        """Test that missing required fields are properly handled"""
        # Test None inputs
        result = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type=OPENAGIActionType.READ_STATE.value,
            inputs=None,  # None inputs
            suggested_changes={"change": "value"},
            explanation="Test explanation"
        )
        
        # Should be rejected for None inputs
        assert result["error_code"] == "MISSING_INPUTS"
        
        # Test None suggested_changes
        result = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type=OPENAGIActionType.READ_STATE.value,
            inputs={"test": "data"},
            suggested_changes=None,  # None changes
            explanation="Test explanation"
        )
        
        # Should be rejected for None suggested_changes
        assert result["error_code"] == "MISSING_SUGGESTED_CHANGES"
        
        # Test missing explanation
        result = self.router.route_submit_agi_observation(
            role=OPENAGIRole.SYSTEM.value,
            action_type=OPENAGIActionType.READ_STATE.value,
            inputs={"test": "data"},
            suggested_changes={"change": "value"},
            explanation=""  # Empty explanation
        )
        
        # Should be rejected for empty explanation
        assert result["error_code"] == "MISSING_EXPLANATION"


if __name__ == "__main__":
    pytest.main([__file__])