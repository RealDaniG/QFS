"""
Tests for OPEN-AGI Role Enforcer implementation
"""
import pytest
from src.auth.open_agi_role import OPENAGIRoleEnforcer, OPENAGIRole, OPENAGIActionType
from src.libs.CertifiedMath import CertifiedMath


class TestOPENAGIRoleEnforcer:
    """Test suite for OPEN-AGI Role Enforcer"""

    def test_role_enforcer_initialization(self):
        """Test that OPEN-AGI Role Enforcer initializes correctly"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        
        assert enforcer is not None
        assert enforcer.cm == cm
        assert enforcer.proposals == []
        assert enforcer.log_entries == []

    def test_authorize_action_system_role(self):
        """Test authorization for SYSTEM role"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        
        # SYSTEM role should be authorized for READ_STATE
        result = enforcer.authorize_action(
            role=OPENAGIRole.SYSTEM,
            action_type=OPENAGIActionType.READ_STATE,
            inputs={"query": "test"},
            deterministic_timestamp=1234567890
        )
        
        assert result["authorized"] == True
        assert "restrictions" in result
        
        # SYSTEM role should NOT be authorized for RUN_SIMULATION
        result = enforcer.authorize_action(
            role=OPENAGIRole.SYSTEM,
            action_type=OPENAGIActionType.RUN_SIMULATION,
            inputs={"params": "test"},
            deterministic_timestamp=1234567891
        )
        
        assert result["authorized"] == False
        assert "reason" in result

    def test_authorize_action_simulator_role(self):
        """Test authorization for SIMULATOR role"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        
        # SIMULATOR role should be authorized for READ_STATE
        result = enforcer.authorize_action(
            role=OPENAGIRole.SIMULATOR,
            action_type=OPENAGIActionType.READ_STATE,
            inputs={"query": "test"},
            deterministic_timestamp=1234567890
        )
        
        assert result["authorized"] == True
        
        # SIMULATOR role should be authorized for RUN_SIMULATION
        result = enforcer.authorize_action(
            role=OPENAGIRole.SIMULATOR,
            action_type=OPENAGIActionType.RUN_SIMULATION,
            inputs={"params": "test"},
            deterministic_timestamp=1234567891
        )
        
        assert result["authorized"] == True
        
        # SIMULATOR role should NOT be authorized for PROPOSE_INTERVENTION
        result = enforcer.authorize_action(
            role=OPENAGIRole.SIMULATOR,
            action_type=OPENAGIActionType.PROPOSE_INTERVENTION,
            inputs={"proposal": "test"},
            deterministic_timestamp=1234567892
        )
        
        assert result["authorized"] == False

    def test_authorize_action_proposer_role(self):
        """Test authorization for PROPOSER role"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        
        # PROPOSER role should be authorized for all actions
        for action_type in OPENAGIActionType:
            result = enforcer.authorize_action(
                role=OPENAGIRole.PROPOSER,
                action_type=action_type,
                inputs={"test": "data"},
                deterministic_timestamp=1234567890
            )
            
            assert result["authorized"] == True

    def test_submit_proposal(self):
        """Test submitting a proposal"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        
        # Only PROPOSER role can submit proposals
        simulation_results = {"outcome": "positive"}
        proposed_changes = {"param": "new_value"}
        
        # This should work
        proposal = enforcer.submit_proposal(
            role=OPENAGIRole.PROPOSER,
            action_type=OPENAGIActionType.PROPOSE_INTERVENTION,
            inputs={"target": "reward_rate"},
            simulation_results=simulation_results,
            proposed_changes=proposed_changes,
            explanation="Test proposal",
            deterministic_timestamp=1234567890
        )
        
        assert proposal is not None
        assert proposal.proposal_id is not None
        assert len(proposal.proposal_id) > 0
        assert proposal.action_type == OPENAGIActionType.PROPOSE_INTERVENTION
        assert proposal.simulation_results == simulation_results
        assert proposal.proposed_changes == proposed_changes
        assert len(enforcer.proposals) == 1
        
        # Test getting proposals
        proposals_result = enforcer.get_proposals()
        assert proposals_result["total_count"] == 1
        assert len(proposals_result["proposals"]) == 1

    def test_activity_log(self):
        """Test activity logging"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        
        # Perform some actions
        enforcer.authorize_action(
            role=OPENAGIRole.SYSTEM,
            action_type=OPENAGIActionType.READ_STATE,
            inputs={"query": "test"},
            deterministic_timestamp=1234567890
        )
        
        enforcer.authorize_action(
            role=OPENAGIRole.SYSTEM,
            action_type=OPENAGIActionType.RUN_SIMULATION,
            inputs={"params": "test"},
            deterministic_timestamp=1234567891
        )
        
        # Check activity log
        log_result = enforcer.get_activity_log()
        # Should have 3 entries: 2 authorizations + 1 proposal submission
        assert log_result["total_count"] >= 2
        assert len(log_result["log_entries"]) >= 2
        
        # Test filtering by role
        role_filtered = enforcer.get_activity_log(role=OPENAGIRole.SYSTEM)
        # SYSTEM role should have at least 2 entries (the authorizations)
        assert role_filtered["total_count"] >= 2
        
        # Test filtering by action type
        action_filtered = enforcer.get_activity_log(action_type=OPENAGIActionType.READ_STATE)
        assert action_filtered["total_count"] == 1

    def test_deterministic_behavior(self):
        """Test that the enforcer behaves deterministically"""
        cm = CertifiedMath()
        
        # Create two enforcers
        enforcer1 = OPENAGIRoleEnforcer(cm)
        enforcer2 = OPENAGIRoleEnforcer(cm)
        
        # Perform identical actions
        inputs = {"test": "data"}
        
        result1 = enforcer1.authorize_action(
            role=OPENAGIRole.SYSTEM,
            action_type=OPENAGIActionType.READ_STATE,
            inputs=inputs,
            deterministic_timestamp=1234567890
        )
        
        result2 = enforcer2.authorize_action(
            role=OPENAGIRole.SYSTEM,
            action_type=OPENAGIActionType.READ_STATE,
            inputs=inputs,
            deterministic_timestamp=1234567890
        )
        
        # Verify deterministic behavior
        # Note: Log IDs will be different because they're based on instance-specific data
        assert result1["authorized"] == result2["authorized"]


if __name__ == "__main__":
    pytest.main([__file__])