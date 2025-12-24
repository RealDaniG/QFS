"""
test_governance_replay.py - End-to-End Replay Validation for Governance Contracts

This test suite executes a full governance lifecycle (Proposal -> Vote -> Tally),
exports the logs/proofs, wipes state, and replays identical inputs to verify:
1. Bit-for-bit identical Proof hashes.
2. Identical logic trace.
3. Vote Tally correctness.
"""

import pytest
import json
import sys
from typing import List, Dict, Any

# Adjust path to find core modules
sys.path.append("d:/AI AGENT CODERV1/QUANTUM CURRENCY/QFS/V13")

from v13.policy.governance.ProposalEngine import ProposalEngine, ProposalStatus
from v13.policy.governance.VoteEngine import VoteEngine, VoteChoice
from v13.libs.CertifiedMath import BigNum128, CertifiedMath


class MockRegistry:
    def __init__(self):
        self.params = {}

    def update_parameter(self, key, val, pid):
        self.params[key] = val


@pytest.fixture
def governance_stack():
    cm = CertifiedMath()
    prop_engine = ProposalEngine()
    vote_engine = VoteEngine(certified_math=cm)
    return prop_engine, vote_engine, cm


def test_governance_lifecycle_determinism(governance_stack):
    prop_engine, vote_engine, cm = governance_stack
    log_list_run1 = []

    # 1. Create Proposal
    payload = {"action": "PARAMETER_CHANGE", "key": "MINT_RATE", "value": 500}
    prop_id = prop_engine.create_proposal(
        title="Increase Mint Rate",
        description="Boost rate to 500",
        execution_payload=payload,
        proposer_id="user_alice",
        log_list=log_list_run1,
    )

    assert prop_id is not None

    # 2. Cast Votes
    # Alice: FOR, 1000 weight
    vote_engine.cast_vote(
        prop_id, "user_alice", VoteChoice.FOR, BigNum128.from_int(1000), log_list_run1
    )

    # Bob: AGAINST, 400 weight
    vote_engine.cast_vote(
        prop_id, "user_bob", VoteChoice.AGAINST, BigNum128.from_int(400), log_list_run1
    )

    # Charlie: ABSTAIN, 50 weight
    vote_engine.cast_vote(
        prop_id,
        "user_charlie",
        VoteChoice.ABSTAIN,
        BigNum128.from_int(50),
        log_list_run1,
    )

    # 3. Tally
    quorum = BigNum128.from_int(100)
    tally_proof_1 = vote_engine.tally_votes(prop_id, quorum, log_list_run1)

    assert tally_proof_1.outcome == "PASSED"
    assert tally_proof_1.total_votes == 3
    assert tally_proof_1.scores["FOR"] == "1000.000000000000000000"

    # --- REPLAY RUN ---

    log_list_run2 = []
    prop_engine_2, vote_engine_2, cm_2 = (
        governance_stack  # Reusing same might be dirty if state leaked, better to recreate or manually clear
    )

    # Wipe state (simulating fresh start)
    prop_engine_2 = ProposalEngine()
    vote_engine_2 = VoteEngine(certified_math=cm_2)

    # REPLAY SAME PROPOSAL
    prop_id_2 = prop_engine_2.create_proposal(
        title="Increase Mint Rate",
        description="Boost rate to 500",
        execution_payload=payload,
        proposer_id="user_alice",
        log_list=log_list_run2,
    )

    assert prop_id_2 == prop_id

    # REPLAY SAME VOTES
    vote_engine_2.cast_vote(
        prop_id_2, "user_alice", VoteChoice.FOR, BigNum128.from_int(1000), log_list_run2
    )
    vote_engine_2.cast_vote(
        prop_id_2,
        "user_bob",
        VoteChoice.AGAINST,
        BigNum128.from_int(400),
        log_list_run2,
    )
    vote_engine_2.cast_vote(
        prop_id_2,
        "user_charlie",
        VoteChoice.ABSTAIN,
        BigNum128.from_int(50),
        log_list_run2,
    )

    tally_proof_2 = vote_engine_2.tally_votes(prop_id_2, quorum, log_list_run2)

    # 4. Verify Identity

    # Proof Hashes must match
    assert tally_proof_1.tally_hash == tally_proof_2.tally_hash

    # Full Logs must match
    # Removing timestamps/non-det fields if any (in this code, everything is det)
    json_1 = json.dumps(log_list_run1, sort_keys=True)
    json_2 = json.dumps(log_list_run2, sort_keys=True)

    assert json_1 == json_2


if __name__ == "__main__":
    # Manual run setup
    try:
        cm = CertifiedMath()
        pe = ProposalEngine()
        ve = VoteEngine(cm)
        test_governance_lifecycle_determinism((pe, ve, cm))
        print("Governance Replay Test PASSED: Bit-exact reproduction confirmed.")
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)
