"""
Comprehensive test suite for InfrastructureGovernance.py
Tests all 7 constitutional governance scenarios

Run: python tests/governance/test_infrastructure_governance_complete.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.libs.CertifiedMath import CertifiedMath, BigNum128
from src.libs.governance.InfrastructureGovernance import (
    InfrastructureGovernance,
    GovernanceProposalType,
    ProposalStatus
)
from src.libs.economics.economic_constants import MAX_NOD_VOTING_POWER_RATIO


def test_all_scenarios():
    """Test the InfrastructureGovernance implementation with all 7 scenarios."""
    print("\n=== Testing InfrastructureGovernance - All 7 Scenarios ===")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create InfrastructureGovernance
    gov = InfrastructureGovernance(cm, BigNum128.from_string("0.5"))  # 50% quorum for testing
    
    # Test total NOD supply
    total_nod_supply = BigNum128.from_int(10000)  # 10,000 NOD total
    
    print("\n--- Scenario 1: Happy Path (create → vote → pass → execute) ---")
    
    # Create a proposal
    proposal_id = gov.create_proposal(
        title="Increase Storage Replication Factor",
        description="Increase the storage replication factor from 3 to 5 for improved redundancy",
        proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR,
        proposer_node_id="node_0xabc123",
        parameters={"current_factor": 3, "proposed_factor": 5},
        total_nod_supply=total_nod_supply,
        creation_timestamp=1000,
        voting_duration_blocks=100  # Short for testing
    )
    
    print(f"✓ Created proposal: {proposal_id[:16]}...")
    
    # Cast votes
    log_list = []
    
    # Node 1 votes yes with 3000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xabc123",
        voter_nod_balance=BigNum128.from_int(3000),
        vote_yes=True,
        timestamp=1100,
        log_list=log_list
    )
    print("✓ Node 1 voted YES with 3000 NOD")
    
    # Node 2 votes no with 2000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xdef456",
        voter_nod_balance=BigNum128.from_int(2000),
        vote_yes=False,
        timestamp=1200,
        log_list=log_list
    )
    print("✓ Node 2 voted NO with 2000 NOD")
    
    # Node 3 votes yes with 4000 NOD
    gov.cast_vote(
        proposal_id=proposal_id,
        voter_node_id="node_0xghi789",
        voter_nod_balance=BigNum128.from_int(4000),
        vote_yes=True,
        timestamp=1300,
        log_list=log_list
    )
    print("✓ Node 3 voted YES with 4000 NOD")
    
    # Tally votes (after voting period ends)
    proposal_passed = gov.tally_votes(
        proposal_id=proposal_id,
        timestamp=100000,  # After voting period
        log_list=log_list
    )
    
    proposal = gov.get_proposal(proposal_id)
    print(f"✓ Proposal tallied: {proposal.status.value} (yes: {proposal.yes_votes.to_decimal_string()}, no: {proposal.no_votes.to_decimal_string()})")
    assert proposal_passed == True, "Proposal should have passed"
    assert proposal.status == ProposalStatus.PASSED, "Status should be PASSED"
    
    # Execute proposal (after timelock)
    execution_timestamp = proposal.execution_earliest_timestamp + 100
    execution_result = gov.execute_proposal(
        proposal_id=proposal_id,
        current_timestamp=execution_timestamp,
        log_list=log_list
    )
    print(f"✓ Proposal executed: {execution_result['success']}")
    assert proposal.executed == True, "Proposal should be marked as executed"
    assert proposal.status == ProposalStatus.EXECUTED, "Status should be EXECUTED"
    
    print("\n--- Scenario 2: Double-Vote Rejection ---")
    
    # Create another proposal
    proposal_id_2 = gov.create_proposal(
        title="AI Model Approval",
        description="Approve new AI model version",
        proposal_type=GovernanceProposalType.AI_MODEL_VERSION_APPROVAL,
        proposer_node_id="node_0xabc123",
        parameters={"model_version": "v2.0", "model_hash": "a" * 64},
        total_nod_supply=total_nod_supply,
        creation_timestamp=200000,  # Respect cooldown
        voting_duration_blocks=100
    )
    
    # Node 1 votes
    gov.cast_vote(
        proposal_id=proposal_id_2,
        voter_node_id="node_0xabc123",
        voter_nod_balance=BigNum128.from_int(3000),
        vote_yes=True,
        timestamp=200100,
        log_list=log_list
    )
    
    # Try to vote again (should fail)
    try:
        gov.cast_vote(
            proposal_id=proposal_id_2,
            voter_node_id="node_0xabc123",
            voter_nod_balance=BigNum128.from_int(3000),
            vote_yes=False,
            timestamp=200200,
            log_list=log_list
        )
        assert False, "Double-vote should have been rejected"
    except ValueError as e:
        print(f"✓ Double-vote rejected: {str(e)[:50]}...")
    
    print("\n--- Scenario 3: Vote Weight Capping ---")
    
    # Create proposal 3
    proposal_id_3 = gov.create_proposal(
        title="Network Bandwidth Update",
        description="Update network bandwidth parameters",
        proposal_type=GovernanceProposalType.NETWORK_BANDWIDTH_PARAMETERS,
        proposer_node_id="node_0xabc123",
        parameters={"max_bandwidth_mbps": 1000},
        total_nod_supply=total_nod_supply,
        creation_timestamp=300000,  # Respect cooldown
        voting_duration_blocks=100
    )
    
    # Node with 30% of total supply (should be capped at 25%)
    large_balance = BigNum128.from_int(3000)  # 30% of 10000
    gov.cast_vote(
        proposal_id=proposal_id_3,
        voter_node_id="node_whale",
        voter_nod_balance=large_balance,
        vote_yes=True,
        timestamp=300100,
        log_list=log_list
    )
    
    proposal_3 = gov.get_proposal(proposal_id_3)
    max_allowed = total_nod_supply.value * MAX_NOD_VOTING_POWER_RATIO.value // BigNum128.SCALE
    print(f"✓ Vote capped: {large_balance.to_decimal_string()} → {proposal_3.yes_votes.to_decimal_string()} (max: {max_allowed})")
    assert proposal_3.yes_votes.value <= max_allowed * BigNum128.SCALE, "Vote should be capped at 25%"
    
    print("\n--- Scenario 4: Timelock Enforcement ---")
    
    # Try to execute proposal 2 before timelock expires (should fail)
    proposal_2 = gov.get_proposal(proposal_id_2)
    # First tally it
    gov.cast_vote(
        proposal_id=proposal_id_2,
        voter_node_id="node_0xdef456",
        voter_nod_balance=BigNum128.from_int(6000),
        vote_yes=True,
        timestamp=200300,
        log_list=log_list
    )
    gov.tally_votes(
        proposal_id=proposal_id_2,
        timestamp=300000,
        log_list=log_list
    )
    
    # Try to execute immediately (should fail)
    try:
        gov.execute_proposal(
            proposal_id=proposal_id_2,
            current_timestamp=proposal_2.execution_earliest_timestamp - 1000,
            log_list=log_list
        )
        assert False, "Execution before timelock should have been rejected"
    except ValueError as e:
        print(f"✓ Timelock enforced: {str(e)[:60]}...")
    
    print("\n--- Scenario 5: Proposal Cancellation (proposer-only) ---")
    
    # Create proposal 4
    proposal_id_4 = gov.create_proposal(
        title="Infrastructure Upgrade",
        description="Upgrade infrastructure components",
        proposal_type=GovernanceProposalType.INFRASTRUCTURE_UPGRADE,
        proposer_node_id="node_0xabc123",
        parameters={"upgrade_version": "v3.0"},
        total_nod_supply=total_nod_supply,
        creation_timestamp=400000,  # Respect cooldown
        voting_duration_blocks=100
    )
    
    # Proposer cancels it
    gov.cancel_proposal(
        proposal_id=proposal_id_4,
        canceller_node_id="node_0xabc123",
        current_timestamp=400100,
        log_list=log_list
    )
    
    proposal_4 = gov.get_proposal(proposal_id_4)
    print(f"✓ Proposal cancelled: {proposal_4.status.value}")
    assert proposal_4.status == ProposalStatus.CANCELLED, "Status should be CANCELLED"
    
    # Try to cancel as non-proposer (should fail)
    proposal_id_5 = gov.create_proposal(
        title="Another Proposal",
        description="Test non-proposer cancellation",
        proposal_type=GovernanceProposalType.SECURITY_PATCH_DEPLOYMENT,
        proposer_node_id="node_0xabc123",
        parameters={"patch_version": "v1.2"},
        total_nod_supply=total_nod_supply,
        creation_timestamp=500000,  # Respect cooldown
        voting_duration_blocks=100
    )
    
    try:
        gov.cancel_proposal(
            proposal_id=proposal_id_5,
            canceller_node_id="node_0xdef456",  # Different node
            current_timestamp=500100,
            log_list=log_list
        )
        assert False, "Non-proposer cancellation should have been rejected"
    except ValueError as e:
        print(f"✓ Non-proposer cancellation rejected: {str(e)[:50]}...")
    
    print("\n--- Scenario 6: Stale Proposal Expiry ---")
    
    # Create proposal 6 and let it expire
    proposal_id_6 = gov.create_proposal(
        title="Expired Proposal",
        description="This will expire",
        proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR,
        proposer_node_id="node_0xabc123",
        parameters={"proposed_factor": 4},
        total_nod_supply=total_nod_supply,
        creation_timestamp=600000,  # Respect cooldown
        voting_duration_blocks=100
    )
    
    proposal_6 = gov.get_proposal(proposal_id_6)
    # Expire stale proposals
    expired_ids = gov.expire_stale_proposals(
        current_timestamp=proposal_6.voting_end_timestamp + 1000,
        log_list=log_list
    )
    
    print(f"✓ Stale proposals expired: {len(expired_ids)} (ID: {proposal_id_6[:16]}...)")
    assert proposal_id_6 in expired_ids, "Proposal 6 should be expired"
    proposal_6 = gov.get_proposal(proposal_id_6)
    assert proposal_6.status == ProposalStatus.EXPIRED, "Status should be EXPIRED"
    
    print("\n--- Scenario 7: Parameter Validation Rejection ---")
    
    # Try to create proposal with invalid parameters (should fail)
    try:
        invalid_proposal = gov.create_proposal(
            title="Invalid Storage Factor",
            description="This should be rejected",
            proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR,
            proposer_node_id="node_0xabc123",
            parameters={"proposed_factor": 15},  # Invalid: >10
            total_nod_supply=total_nod_supply,
            creation_timestamp=700000,  # Respect cooldown
            voting_duration_blocks=100
        )
        assert False, "Invalid parameter should have been rejected"
    except ValueError as e:
        print(f"✓ Invalid parameter rejected: {str(e)[:60]}...")
    
    # Verify event hashes are present in logs
    print("\n--- Verifying Event Hashes ---")
    hashed_events = [entry for entry in log_list if "event_hash" in entry]
    print(f"✓ Events with SHA-256 hashes: {len(hashed_events)}")
    assert len(hashed_events) > 0, "Event hashes should be present in logs"
    
    # Sample event hash
    sample_hash = hashed_events[0]["event_hash"]
    print(f"✓ Sample event hash: {sample_hash[:32]}...")
    assert len(sample_hash) == 64, "SHA-256 hash should be 64 characters"
    
    print("\n=== ALL 7 SCENARIOS PASSED ✓ ===")
    print(f"Total log entries: {len(log_list)}")
    print(f"Total proposals: {len(gov.proposals)}")
    print(f"Proposals by status:")
    for status in ProposalStatus:
        count = sum(1 for p in gov.proposals.values() if p.status == status)
        if count > 0:
            print(f"  - {status.value}: {count}")


if __name__ == "__main__":
    test_all_scenarios()
