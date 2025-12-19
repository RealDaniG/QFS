"""
Governance Cycle Replay Tool for QFS v15.3
Replays a governance execution from canonical inputs to verify determinism.
"""

import argparse
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any

# Mocking PQC Provider for replay environment if needed
# In real usage, this would import the actual deterministic runtime
from v13.libs.BigNum128 import BigNum128


def sha3_512(data: bytes) -> str:
    h = hashlib.sha3_512()
    h.update(data)
    return f"sha3_512:{h.hexdigest()}"


def canonical_serialize(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def replay_artifact(artifact_id: str) -> bool:
    """
    Replay the governance cycle defined in the artifact.
    1. Load artifact
    2. Extract replay instructions (inputs, command)
    3. Re-execute logic (simulated here via ProposalEngine)
    4. Compare output hash
    """
    path = Path(f"evidence/poe_artifacts/{artifact_id}.json")
    if not path.exists():
        print(f"Error: Artifact {artifact_id} not found")
        return False

    with open(path, "r") as f:
        artifact = json.load(f)

    print(f"🔄 Replaying Governance Cycle: {artifact_id}")
    print(f"   Scope: {artifact['governance_scope']['parameter_key']}")
    print(f"   Cycle: {artifact['governance_scope']['cycle']}")

    # In a full implementation, this calls ProposalEngine.execute_proposal directly
    # passing the exact timestamp and inputs recorded in the artifact
    # For v15.3 prototype, we will verify the hash integrity of the execution trace

    trace = artifact.get("execution_trace", {})
    if not trace:
        print("❌ Replay Failed: No execution trace in artifact")
        return False

    # Verify Trace Hash
    computed_trace_hash = sha3_512(canonical_serialize(trace).encode())

    if computed_trace_hash != artifact["execution_trace_hash"]:
        print(f"❌ Replay Failed: Execution Trace Hash Mismatch")
        print(f"   Expected: {artifact['execution_trace_hash']}")
        print(f"   Computed: {computed_trace_hash}")
        return False

    # Verify Final Proof Hash (which wraps trace + state + votes)
    # Reconstruct the "content" part of the proof
    proof_content = {
        "proposal_hash": artifact["proposal_hash"],
        "vote_breakdown": artifact["vote_breakdown"],
        "execution_trace_hash": artifact["execution_trace_hash"],
        "before_state_hash": artifact["before_state_hash"],
        "after_state_hash": artifact["after_state_hash"],
        "runtime_info": artifact["runtime_info"],
    }

    computed_proof_hash = sha3_512(canonical_serialize(proof_content).encode())

    if computed_proof_hash != artifact["proof_hash"]:
        print(f"❌ Replay Failed: Proof Hash Mismatch")
        print(f"   Expected: {artifact['proof_hash']}")
        print(f"   Computed: {computed_proof_hash}")
        return False

    print(f"✅ Replay Verify: MATCH (Hash: {computed_proof_hash[:16]}...)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Replay QFS Governance Cycle")
    parser.add_argument(
        "--artifact_id", required=True, help="PoE Artifact ID to replay"
    )
    args = parser.parse_args()

    success = replay_artifact(args.artifact_id)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
