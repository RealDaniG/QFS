"""
test_proposal_engine.py - Verification for v15 Governance Core

Invariants Verified:
- GOV-I1: Integer-only thresholds (30% quorum, 66% supermajority).
- GOV-I2: Deterministic ID generation (SHA3-512).
- GOV-I3: Proof-of-Execution artifacts generated on finalization.
"""

import sys
import unittest
from typing import Dict, Any

# Ensure v13 root is in path
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
)

from v15.atlas.governance.ProposalEngine import (
    ProposalEngine,
    ProposalKind,
    ProposalStatus,
)
from v15.atlas.governance.GovernanceParameterRegistry import GovernanceParameterRegistry
from v13.libs.BigNum128 import BigNum128


class TestProposalEngineV15(unittest.TestCase):
    def setUp(self):
        self.engine = ProposalEngine()
        self.registry = GovernanceParameterRegistry()

    def test_deterministic_id(self):
        """Verify IDs are deterministic based on content."""
        payload = {"key": "VIRAL_POOL_CAP", "value": 500}

        id1 = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "Title", "Desc", "Alice", payload
        )

        # Exact same content should generate different ID if cycle/nonce changes
        # But here we use default cycle=0.
        # Wait, the engine checks uniqueness or overwrites?
        # My implementation overwrites if ID exists.
        # But ID derivation is deterministic.

        # Let's verify same input -> same ID
        id2 = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "Title", "Desc", "Alice", payload
        )
        self.assertEqual(id1, id2)

        # Change content -> Different ID
        id3 = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "Title", "Desc", "Bob", payload
        )
        self.assertNotEqual(id1, id3)

    def test_integer_thresholds(self):
        """Verify 30% Quorum and 66% Supermajority using pure integers."""
        # Total Stake = 10,000 NOT

        payload = {"key": "VIRAL_POOL_CAP", "value": 500}
        pid = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "Title", "Desc", "Alice", payload
        )

        # 1. Below Quorum (2999 / 10000 = 29%)
        self.engine.cast_vote(pid, "Voter1", "YES", 2999)
        status, _ = self.engine.try_finalize(pid)
        self.assertEqual(status, ProposalStatus.REJECTED)  # Quorum Fail

        # 2. Meet Quorum (3000 / 10000 = 30%)
        # But fail Supermajority (1500 Yes, 1500 No -> 50%)
        pid2 = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "T2", "D", "A", payload, cycle_index=1
        )
        self.engine.cast_vote(pid2, "V1", "YES", 1500)
        self.engine.cast_vote(pid2, "V2", "NO", 1500)
        status2, proof2 = self.engine.try_finalize(pid2)

        self.assertEqual(status2, ProposalStatus.REJECTED)
        self.assertEqual(proof2["result_metrics"]["participation_pct"], 30)
        self.assertEqual(proof2["result_metrics"]["yes_ratio_pct"], 50)

        # 3. Pass (3000 Votes, 2000 Yes, 1000 No -> 66.6% Yes -> 66% integer)
        # 2000 / 3000 = 66% exactly integer division
        # Threshold is 66, so 66 >= 66 Pass.
        pid3 = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "T3", "D", "A", payload, cycle_index=2
        )
        self.engine.cast_vote(pid3, "V1", "YES", 2000)
        self.engine.cast_vote(pid3, "V2", "NO", 1000)
        status3, proof3 = self.engine.try_finalize(pid3)

        self.assertEqual(status3, ProposalStatus.PASSED)
        self.assertEqual(proof3["result_metrics"]["yes_ratio_pct"], 66)
        self.assertIn("payload_hash", proof3)

    def test_execution_and_registry(self):
        """Verify Parameter Change execution updates v15 Registry."""
        payload = {
            "action": "PARAMETER_CHANGE",
            "key": "VIRAL_POOL_CAP",
            "value": 12345,
        }
        # Note: ViralRewardBinder expects BigNum128, registry expects BigNum128.
        # ProposalEngine v15 prototype converts int to BigNum128.

        pid = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "Update Cap", "Desc", "Alice", payload
        )

        # Force Pass
        self.engine.cast_vote(pid, "God", "YES", 8000)  # 80% Yes, 80% Quorum
        self.engine.try_finalize(pid)

        # Execute
        success = self.engine.execute_proposal(pid, self.registry)
        self.assertTrue(success)

        # Verify Registry
        new_cap = self.registry.get("VIRAL_POOL_CAP")
        self.assertEqual(new_cap, BigNum128.from_int(12345))

    def test_immutable_protection(self):
        """Verify v15 Registry blocks immutable updates."""
        payload = {"action": "PARAMETER_CHANGE", "key": "IMMUTABLE_CONST", "value": 1}
        pid = self.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE, "Bad", "Desc", "A", payload
        )

        self.engine.cast_vote(pid, "God", "YES", 8000)
        self.engine.try_finalize(pid)

        # Execute should fail / return False / Log error
        success = self.engine.execute_proposal(pid, self.registry)
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
