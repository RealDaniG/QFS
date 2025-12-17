"""
Tests for OPEN-AGI Role Enforcer implementation
"""
import pytest
from v13.auth.open_agi_role import OPENAGIRoleEnforcer, OPENAGIRole, OPENAGIActionType
from v13.libs.CertifiedMath import CertifiedMath

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
        result = enforcer.authorize_action(role=OPENAGIRole.SYSTEM, action_type=OPENAGIActionType.READ_STATE, inputs={'query': 'test'}, deterministic_timestamp=1234567890)
        assert result['authorized'] == True
        assert 'restrictions' in result
        result = enforcer.authorize_action(role=OPENAGIRole.SYSTEM, action_type=OPENAGIActionType.RUN_SIMULATION, inputs={'params': 'test'}, deterministic_timestamp=1234567891)
        assert result['authorized'] == False
        assert 'reason' in result

    def test_authorize_action_simulator_role(self):
        """Test authorization for SIMULATOR role"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        result = enforcer.authorize_action(role=OPENAGIRole.SIMULATOR, action_type=OPENAGIActionType.READ_STATE, inputs={'query': 'test'}, deterministic_timestamp=1234567890)
        assert result['authorized'] == True
        result = enforcer.authorize_action(role=OPENAGIRole.SIMULATOR, action_type=OPENAGIActionType.RUN_SIMULATION, inputs={'params': 'test'}, deterministic_timestamp=1234567891)
        assert result['authorized'] == True
        result = enforcer.authorize_action(role=OPENAGIRole.SIMULATOR, action_type=OPENAGIActionType.PROPOSE_INTERVENTION, inputs={'proposal': 'test'}, deterministic_timestamp=1234567892)
        assert result['authorized'] == False

    def test_authorize_action_proposer_role(self):
        """Test authorization for PROPOSER role"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        for action_type in sorted(OPENAGIActionType):
            result = enforcer.authorize_action(role=OPENAGIRole.PROPOSER, action_type=action_type, inputs={'test': 'data'}, deterministic_timestamp=1234567890)
            assert result['authorized'] == True

    def test_submit_proposal(self):
        """Test submitting a proposal"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        simulation_results = {'outcome': 'positive'}
        proposed_changes = {'param': 'new_value'}
        proposal = enforcer.submit_proposal(role=OPENAGIRole.PROPOSER, action_type=OPENAGIActionType.PROPOSE_INTERVENTION, inputs={'target': 'reward_rate'}, simulation_results=simulation_results, proposed_changes=proposed_changes, explanation='Test proposal', deterministic_timestamp=1234567890)
        assert proposal is not None
        assert proposal.proposal_id is not None
        assert len(proposal.proposal_id) > 0
        assert proposal.action_type == OPENAGIActionType.PROPOSE_INTERVENTION
        assert proposal.simulation_results == simulation_results
        assert proposal.proposed_changes == proposed_changes
        assert len(enforcer.proposals) == 1
        proposals_result = enforcer.get_proposals()
        assert proposals_result['total_count'] == 1
        assert len(proposals_result['proposals']) == 1

    def test_activity_log(self):
        """Test activity logging"""
        cm = CertifiedMath()
        enforcer = OPENAGIRoleEnforcer(cm)
        enforcer.authorize_action(role=OPENAGIRole.SYSTEM, action_type=OPENAGIActionType.READ_STATE, inputs={'query': 'test'}, deterministic_timestamp=1234567890)
        enforcer.authorize_action(role=OPENAGIRole.SYSTEM, action_type=OPENAGIActionType.RUN_SIMULATION, inputs={'params': 'test'}, deterministic_timestamp=1234567891)
        log_result = enforcer.get_activity_log()
        assert log_result['total_count'] >= 2
        assert len(log_result['log_entries']) >= 2
        role_filtered = enforcer.get_activity_log(role=OPENAGIRole.SYSTEM)
        assert role_filtered['total_count'] >= 2
        action_filtered = enforcer.get_activity_log(action_type=OPENAGIActionType.READ_STATE)
        assert action_filtered['total_count'] == 1

    def test_deterministic_behavior(self):
        """Test that the enforcer behaves deterministically"""
        cm = CertifiedMath()
        enforcer1 = OPENAGIRoleEnforcer(cm)
        enforcer2 = OPENAGIRoleEnforcer(cm)
        inputs = {'test': 'data'}
        result1 = enforcer1.authorize_action(role=OPENAGIRole.SYSTEM, action_type=OPENAGIActionType.READ_STATE, inputs=inputs, deterministic_timestamp=1234567890)
        result2 = enforcer2.authorize_action(role=OPENAGIRole.SYSTEM, action_type=OPENAGIActionType.READ_STATE, inputs=inputs, deterministic_timestamp=1234567890)
        assert result1['authorized'] == result2['authorized']
if __name__ == '__main__':
    pytest.main([__file__])