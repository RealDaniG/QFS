"""Debug governance test timing"""
import sys
import os
import json
import hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from libs.CertifiedMath import CertifiedMath, BigNum128
from libs.governance.InfrastructureGovernance import InfrastructureGovernance, GovernanceProposalType

# Create test snapshots
telemetry = {
    "schema_version": "v1.0",
    "block_height": 1000,
    "telemetry_hash": "a" * 64,
    "nodes": {
        "node_001": {
            "uptime_ratio": 0.95,
            "health_score": 0.95
        },
        "node_002": {
            "uptime_ratio": 0.93,
            "health_score": 0.90
        },
        "node_003": {
            "uptime_ratio": 0.94,
            "health_score": 0.92
        }
    }
}

registry = {
    "schema_version": "1.0",
    "nodes": {
        "node_001": {
            "pqc_public_key": "pk_node_001",
            "pqc_scheme": "Dilithium5",
            "registered_at": 0,
            "status": "active",
            "revoked": False
        },
        "node_002": {
            "pqc_public_key": "pk_node_002",
            "pqc_scheme": "Dilithium5",
            "registered_at": 0,
            "status": "active",
            "revoked": False
        },
        "node_003": {
            "pqc_public_key": "pk_node_003",
            "pqc_scheme": "Dilithium5",
            "registered_at": 0,
            "status": "active",
            "revoked": False
        }
    }
}

# Test governance
cm = CertifiedMath()
governance = InfrastructureGovernance(cm)

# Create proposal
creation_timestamp = 1000
voting_duration_blocks = 100

print(f"Creating proposal with:")
print(f"  creation_timestamp = {creation_timestamp}")
print(f"  voting_duration_blocks = {voting_duration_blocks}")

proposal_id = governance.create_proposal(
    title="Storage Replication Factor Update",
    description="Propose updating storage replication factor",
    proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR,
    proposer_node_id="node_001",
    parameters={"proposed_factor": 3},
    total_nod_supply=BigNum128.from_string("1000000.0"),
    creation_timestamp=creation_timestamp,
    voting_duration_blocks=voting_duration_blocks,
    registry_snapshot=registry,
    telemetry_snapshot=telemetry,
    log_list=[]
)

proposal = governance.proposals[proposal_id]
print(f"\nProposal created:")
print(f"  proposal_id = {proposal_id}")
print(f"  creation_timestamp = {proposal.creation_timestamp}")
print(f"  voting_end_timestamp = {proposal.voting_end_timestamp}")
print(f"  execution_earliest_timestamp = {proposal.execution_earliest_timestamp}")

# Try to tally at different timestamps
timestamps_to_test = [2699, 2700, 2701, 2702, 2800]
for timestamp in timestamps_to_test:
    try:
        result = governance.tally_votes(proposal_id, timestamp, [])
        print(f"  ✓ Tally at {timestamp}: SUCCESS")
    except ValueError as e:
        print(f"  ✗ Tally at {timestamp}: {e}")
