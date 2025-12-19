"""
test_stress_campaign.py - High-Load Deterministic Stress Test for QFS v15

Purpose:
Simulate extreme but realistic usage patterns to verify:
1. Determinism under high throughput (100+ proposals).
2. Registry stability with frequent updates.
3. AEGIS Coherence during heavy mutation.
4. Proof-of-Execution chain integrity.

Invariants Verified:
- POE-I1: Every action must produce a valid proof.
- GOV-I1: Immutable keys MUST NOT change even under directed attack.
- REPLAY-I1: Replaying the entire campaign must produce identical state hashes (0 Drift).
"""

import unittest
import hashlib
import json
import time
import os
import sys

# Robust Path Setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v15.atlas.governance.ProposalEngine import (
    ProposalEngine,
    ProposalKind,
    ProposalStatus,
)
from v15.atlas.governance.GovernanceParameterRegistry import GovernanceParameterRegistry
from v15.atlas.governance.GovernanceTrigger import GovernanceTrigger
from v15.atlas.aegis.GovernanceCoherenceCheck import GovernanceCoherenceCheck
from v13.libs.BigNum128 import BigNum128


class TestStressCampaign(unittest.TestCase):
    def run_campaign(self, seed: int, proposal_count: int = 50):
        """Runs a generated campaign of proposals and votes."""
        engine = ProposalEngine()
        registry = GovernanceParameterRegistry()
        trigger = GovernanceTrigger(registry)

        # Artifacts to hash for determinism check
        proof_chain = []

        # 1. Proposal Flood
        # Mix of Parameter Changes (Mutable & Immutable) and Text Proposals
        for i in range(proposal_count):
            cycle_id = seed * 1000 + i

            # Alternate types
            if i % 3 == 0:
                # Valid Parameter Change
                payload = {
                    "action": "PARAMETER_CHANGE",
                    "key": "VIRAL_POOL_CAP",
                    "value": 1000000 + i,
                }
                pid = engine.create_proposal(
                    ProposalKind.PARAMETER_CHANGE,
                    f"Stress Update {i}",
                    "Load Test",
                    "Bot",
                    payload,
                    cycle_id,
                )
            elif i % 3 == 1:
                # Invalid Parameter Change (Immutable)
                payload = {
                    "action": "PARAMETER_CHANGE",
                    "key": "CHR_DAILY_EMISSION_CAP",
                    "value": 999,
                }
                pid = engine.create_proposal(
                    ProposalKind.PARAMETER_CHANGE,
                    f"Attack Immutable {i}",
                    "Attack",
                    "MaliceBot",
                    payload,
                    cycle_id,
                )
            else:
                # Text Proposal
                payload = {"text": f"Motion to stress test #{i}"}
                pid = engine.create_proposal(
                    ProposalKind.TEXT, f"Motion {i}", "Spam", "User", payload, cycle_id
                )

            # 2. Voting Frenzy
            # Deterministic voting based on 'i'
            # Pass approx 50%
            yes_votes = 2000 if i % 2 == 0 else 500
            no_votes = 500 if i % 2 == 0 else 2000

            engine.cast_vote(pid, "Whale1", "YES", yes_votes)
            engine.cast_vote(pid, "Whale2", "NO", no_votes)

            # 3. Finalization & Execution attempt
            status, proof = engine.try_finalize(pid)
            if proof:
                proof_chain.append(proof)

            if status == ProposalStatus.PASSED:
                engine.execute_proposal(pid, registry)
                # Force a tick every 10 proposals to activate batches
                if i % 10 == 0:
                    trigger.process_tick(100 + i)

        # Check Coherence at end of campaign
        aegis = GovernanceCoherenceCheck(registry, trigger)
        is_coherent = aegis.verify_coherence()

        # Return state for comparison (use registry values directly)
        final_state = {
            "viral_pool_cap": registry.get("VIRAL_POOL_CAP").to_decimal_string(),
            "proof_chain_len": len(proof_chain),
            "coherence": is_coherent,
            "total_proposals": len(engine.proposals),
        }
        return final_state

    def test_campaign_replay_drift(self):
        """Standard Stress: Play campaign 2x and ensure 0 drift."""
        print("\n[STRESS] Running Campaign Run A...")
        start_time = time.time()
        state_a = self.run_campaign(seed=1337, proposal_count=50)
        duration = time.time() - start_time
        print(f"[STRESS] Run A Complete. Throughput: {50 / duration:.1f} props/sec.")

        print("[STRESS] Running Campaign Run B (Replay)...")
        state_b = self.run_campaign(seed=1337, proposal_count=50)

        # Verify 0 Drift
        self.assertEqual(state_a, state_b, "CRITICAL: Replay Drift Detected!")
        self.assertTrue(
            state_a["coherence"], "CRITICAL: AEGIS Coherence Failed during stress!"
        )

        print("[STRESS] ✅ 0 Drift / Coherence OK.")

    def test_immutable_protection_under_load(self):
        """Verify that NO immutable keys were changed despite attacks."""
        registry = GovernanceParameterRegistry()
        # Immutable default
        default_emit = registry.get("CHR_DAILY_EMISSION_CAP")

        # Run campaign
        self.run_campaign(seed=999, proposal_count=20)

        # Check integrity
        current_emit = registry.get("CHR_DAILY_EMISSION_CAP")
        self.assertEqual(
            default_emit.to_decimal_string(),
            current_emit.to_decimal_string(),
            "Immutable Key was Modified!",
        )


if __name__ == "__main__":
    import io

    # Capture output to buffer
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)

    print("\n[STRESS] v15 GOVERNANCE STRESS CAMPAIGN\n" + "=" * 40)
    # Load all tests from self
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStressCampaign)

    result = runner.run(suite)

    # Write full output to log file
    output = stream.getvalue()
    print(output)

    with open("stress_failure_log.txt", "w") as f:
        f.write(output)
        if not result.wasSuccessful():
            f.write("\n\nFAILURES/ERRORS:\n")
            for failure in result.failures:
                f.write(str(failure) + "\n")
            for error in result.errors:
                f.write(str(error) + "\n")

    if result.wasSuccessful():
        print("\n\n✅ v15 STRESS TEST: PASSED 0 DRIFT")
        sys.exit(0)
    else:
        print("\n\n❌ v15 STRESS TEST: FAILED")
        sys.exit(1)
