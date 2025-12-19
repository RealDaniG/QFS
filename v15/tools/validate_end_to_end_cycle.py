"""
End-to-End Governance Cycle Validation Tool
Orchestrates a full governance lifecycle to verify PoE integration, indexing, and replayability.

Flow:
1. Create Proposal
2. Vote
3. Execute (Triggers PoE generation + Indexing)
4. Verify PoE Artifact via verify_poe.py
5. Verify Index Entry
6. Verify Deterministic Replay via replay_gov_cycle.py
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Tuple

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from v15.atlas.governance.GovernanceParameterRegistry import GovernanceParameterRegistry
from v15.atlas.governance.ProposalEngine import ProposalEngine
from v13.libs.BigNum128 import BigNum128
from v15.tools.governance_index_manager import get_index_manager
import traceback


def run_validation():
    print("\n🚀 Starting End-to-End Governance Cycle Validation")
    print("=" * 60)

    # 1. Setup Environment
    registry = GovernanceParameterRegistry()
    engine = ProposalEngine()

    # 2. Create Proposal
    print("\n📝 Creating Proposal...")
    try:
        # Prepare payload
        payload = {
            "key": "VIRAL_POOL_CAP",
            "value": 2000,
        }  # Need to use Enum member if ProposalEngine expects it,
        # or rely on string if engine is loose.
        # Inspecting ProposalEngine shows it accesses kind.value, so must be Enum.
        from v15.atlas.governance.ProposalEngine import ProposalKind

        proposal_id = engine.create_proposal(
            kind=ProposalKind.PARAMETER_CHANGE,
            title="E2E Validation Proposal",
            description="Validating PoE integration",
            proposer="validator_wallet_01",
            execution_payload=payload,
        )

        # Helper to get the full object if create_proposal only returns ID
        proposal = engine.proposals[proposal_id]
        print(f"   Created Proposal ID: {proposal.id}")
    except Exception as e:
        print(f"❌ Proposal Creation Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 3. Vote
    print("\n🗳️  Voting...")
    engine.cast_vote(proposal.id, "validator_wallet_01", "YES", weight=2000)
    engine.cast_vote(proposal.id, "validator_wallet_02", "YES", weight=2000)

    # 3b. Finalize
    print("\n⚖️  Finalizing Tally...")
    status, proof = engine.try_finalize(proposal.id)
    print(f"   Final Status: {status}")
    if status.value != "PASSED":
        print(f"❌ Proposal Finalization Failed: {status} (Proof: {proof})")
        sys.exit(1)

    # 4. Execute
    print("\n⚙️  Executing...")
    try:
        success = engine.execute_proposal(proposal.id, registry)
        if not success:
            print("❌ Execution Failed (Returned False)")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Execution Failed with Exception: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Retrieve the artifact ID from the executed proposal (simulated or looked up)
    # Since ProposalEngine stores it on the proposal object in memory, let's grab it
    prop_obj = engine.proposals[proposal.id]
    artifact_id = getattr(prop_obj, "poe_artifact_id", None)

    if not artifact_id:
        print("❌ Verification Failed: No PoE Artifact ID found on executed proposal")
        sys.exit(1)

    print(f"   Execution Successful. Artifact ID: {artifact_id}")

    # 5. Verify PoE Artifact (using v15/tools/verify_poe.py)
    print("\n🔍 Verifying PoE Artifact Structure & Crypto...")
    cmd_verify = [
        sys.executable,
        "v15/tools/verify_poe.py",
        "--artifact_id",
        artifact_id,
    ]
    res_verify = subprocess.run(cmd_verify, capture_output=True, text=True)

    if res_verify.returncode != 0:
        print("❌ verify_poe.py Failed:")
        print(res_verify.stdout)
        print(res_verify.stderr)
        sys.exit(1)
    else:
        print("   ✅ Artifact Verification Passed")

    # 6. Verify Index Entry
    print("\n📇 Verifying Governance Index...")
    index_manager = get_index_manager()
    entries = index_manager.get_by_scope("VIRAL_POOL_CAP")

    valid_entry = next((e for e in entries if e["artifact_id"] == artifact_id), None)

    if not valid_entry:
        print("❌ Index Verification Failed: Artifact not found in index")
        sys.exit(1)

    if not index_manager.verify_chain():
        print("❌ Index Verification Failed: Hash chain invalid")
        sys.exit(1)

    print(f"   ✅ Index Entry Found (Seq: {valid_entry['sequence_number']})")
    print("   ✅ Hash Chain Integrity Verified")

    # 7. Verify Deterministic Replay (using v15/tools/replay_gov_cycle.py)
    print("\n🔄 Verifying Deterministic Replay...")
    cmd_replay = [
        sys.executable,
        "v15/tools/replay_gov_cycle.py",
        "--artifact_id",
        artifact_id,
    ]
    res_replay = subprocess.run(cmd_replay, capture_output=True, text=True)

    if res_replay.returncode != 0:
        print("❌ replay_gov_cycle.py Failed:")
        print(res_replay.stdout)
        print(res_replay.stderr)
        sys.exit(1)
    else:
        print("   ✅ Replay Verification Passed")

    print("\n" + "=" * 60)
    print("✅ E2E VALIDATION SUCCESSFUL: System is Structurally Verifiable.")
    print("=" * 60)


if __name__ == "__main__":
    run_validation()
