"""
test_governance_replay.py - Autonomous Regression for v15 Governance

Purpose:
- Replay a full governance cycle (Proposal -> Vote -> Finalize -> Execute).
- Verify Bit-for-Bit Determinism of Proof-of-Execution artifacts.
- Verify Integration with v13 Economics (ViralRewardBinder).

Invariants:
- GOV-R1: Replaying the same inputs must yield identical Proof Artifacts.
- GOV-R2: Executing a Parameter Change Proposal must update the Registry.
- GOV-R3: ViralRewardBinder must immediately reflect the Registry state.
"""

import sys
import os
import json
import hashlib
import unittest

# Ensure v13 root is in path
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
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.governance.RewardAllocator import RewardAllocator
from v13.atlas.economics.ViralRewardBinder import ViralRewardBinder


from v15.atlas.governance.GovernanceTrigger import GovernanceTrigger


class TestGovernanceReplay(unittest.TestCase):
    def run_cycle(self, cycle_seed: int):
        """Runs a deterministic governance cycle and returns state hashes + binder cap."""
        engine = ProposalEngine()
        registry = GovernanceParameterRegistry()
        trigger = GovernanceTrigger(registry)  # Added in Stage 6

        # Setup Binder with v15 Registry via Trigger
        cm = CertifiedMath()
        allocator = RewardAllocator(cm)
        binder = ViralRewardBinder(cm, allocator, trigger=trigger)

        metrics = {"proofs": []}

        # 1. Create Proposal (Change Cap to 500,000)
        # Deterministic ID relies on content + cycle
        payload = {
            "action": "PARAMETER_CHANGE",
            "key": "VIRAL_POOL_CAP",
            "value": 500_000,
        }
        pid = engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE,
            "Lower Cap",
            "Desc",
            "ProposerA",
            payload,
            cycle_index=cycle_seed,
        )

        # 2. Vote (Pass)
        # Total Stake 10000. 3000 Votes. 2000 Yes.
        engine.cast_vote(pid, "V1", "YES", 2000)
        engine.cast_vote(pid, "V2", "NO", 1000)

        # 3. Finalize
        status, proof = engine.try_finalize(pid)
        metrics["proofs"].append(proof)

        # 4. Execute
        if status == ProposalStatus.PASSED:
            engine.execute_proposal(pid, registry)
            # v15: Force Trigger Tick to activate new parameters
            trigger.process_tick(100)

        # 5. Capture Binder State
        binder_cap = binder.VIRAL_POOL_CAP.to_decimal_string()

        return metrics, binder_cap

    def test_bit_for_bit_replay(self):
        """Verify that running the cycle twice produces identical artifacts."""
        print("Running Cycle A...")
        metrics_a, binder_cap_a = self.run_cycle(1)

        print("Running Cycle B (Replay)...")
        metrics_b, binder_cap_b = self.run_cycle(1)

        # Hash Artifacts
        json_a = json.dumps(metrics_a, sort_keys=True)
        hash_a = hashlib.sha3_512(json_a.encode("utf-8")).hexdigest()

        json_b = json.dumps(metrics_b, sort_keys=True)
        hash_b = hashlib.sha3_512(json_b.encode("utf-8")).hexdigest()

        print(f"Hash A: {hash_a[:16]}...")
        print(f"Hash B: {hash_b[:16]}...")

        self.assertEqual(hash_a, hash_b, "Governance Cycle is NOT deterministic!")
        self.assertEqual(binder_cap_a, binder_cap_b, "Binder state diverged!")

        # Verify the change actually happened
        # 500,000 BigNum128 string
        expected = BigNum128.from_int(500_000).to_decimal_string()
        self.assertEqual(binder_cap_a, expected, "Binder did not update from Registry!")

        print("Replay Test Verified: Deterministic & Integrated.")

    def test_cycle_divergence(self):
        """Verify that different inputs yield different valid proofs (Sensitivity check)."""
        metrics_1, _ = self.run_cycle(1)
        metrics_2, _ = self.run_cycle(2)  # Different Cycle Index -> Different ID

        self.assertNotEqual(metrics_1, metrics_2)
        print("Sensitivity Verified: Cycle index impacts state.")


if __name__ == "__main__":
    unittest.main()
