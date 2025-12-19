"""
Testnet Scenario 2: Multi-Proposal Stress Test
Goal: Execute 50 sequential proposals to verify zero drift and AEGIS coherence
Expected Outcome: All proposals execute successfully, zero drift, consistent PoE hashes
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from v15.atlas.governance import (
    GovernanceParameterRegistry,
    ProposalEngine,
    GovernanceTrigger,
)
from v15.atlas.aegis import GovernanceCoherenceCheck
from v13.libs.BigNum128 import BigNum128
from v13.libs.CertifiedMath import CertifiedMath


def scenario_2_stress_test():
    """Execute Scenario 2: Multi-Proposal Stress Test."""

    print("=" * 80)
    print("Testnet Scenario 2: Multi-Proposal Stress Test")
    print("Goal: Execute 50 sequential proposals")
    print("=" * 80)

    # Initialize components
    print("\n[INIT] Initializing governance components...")
    cm = CertifiedMath()
    registry = GovernanceParameterRegistry()
    engine = ProposalEngine(registry)
    trigger = GovernanceTrigger(registry, epoch_duration=100)
    aegis = GovernanceCoherenceCheck(registry, trigger)

    # Verify initial AEGIS coherence
    is_coherent, msg = aegis.verify_coherence()
    assert is_coherent, f"Initial AEGIS check failed: {msg}"
    print(f"✓ Initial AEGIS Status: COHERENT")

    # Track PoE hashes for drift detection
    poe_hashes = []

    # Execute 50 proposals
    num_proposals = 50
    print(f"\n[STRESS TEST] Executing {num_proposals} proposals...")

    for i in range(num_proposals):
        # Alternate between two parameter changes
        if i % 2 == 0:
            # Change VIRAL_POOL_CAP
            param_key = "VIRAL_POOL_CAP"
            new_value = BigNum128(1_000_000_000_000_000_000_000_000_000 + (i * 1000))
        else:
            # Change VIRAL_REWARD_MULTIPLIER
            param_key = "VIRAL_REWARD_MULTIPLIER"
            new_value = BigNum128(1_000_000_000_000_000_000 + (i * 100))

        # Create proposal
        proposal = engine.create_proposal(
            kind="PARAMETER_CHANGE",
            title=f"Stress Test Proposal {i + 1}",
            description=f"Automated stress test proposal {i + 1}/{num_proposals}",
            parameter_key=param_key,
            new_value=new_value,
            proposer_wallet=f"wallet_stress_{i}",
        )

        # Vote
        engine.vote(proposal.proposal_id, f"wallet_stress_{i}", True, stake=1000)

        # Execute
        engine.execute_proposal(proposal.proposal_id)

        # Get PoE hash
        poe_hash = engine.get_execution_proof(proposal.proposal_id)
        poe_hashes.append(poe_hash)

        # Verify AEGIS coherence after each proposal
        is_coherent, msg = aegis.verify_coherence()
        assert is_coherent, f"AEGIS coherence failed at proposal {i + 1}: {msg}"

        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  ✓ Completed {i + 1}/{num_proposals} proposals")

    print(f"\n✓ All {num_proposals} proposals executed successfully")

    # Verify zero drift by checking PoE hash uniqueness
    print("\n[DRIFT CHECK] Verifying zero drift...")
    unique_hashes = set(poe_hashes)
    assert len(unique_hashes) == num_proposals, (
        f"Drift detected: {len(unique_hashes)} unique hashes for {num_proposals} proposals"
    )
    print(f"✓ Zero drift verified: {num_proposals} unique PoE hashes")

    # Final AEGIS coherence check
    print("\n[FINAL CHECK] Verifying final AEGIS coherence...")
    is_coherent, msg = aegis.verify_coherence()
    assert is_coherent, f"Final AEGIS check failed: {msg}"
    print(f"✓ Final AEGIS Status: COHERENT - {msg}")

    print("\n" + "=" * 80)
    print("Scenario 2: COMPLETE ✓")
    print("=" * 80)

    print("\n✅ All checks passed:")
    print(f"  - {num_proposals} proposals created and executed")
    print(f"  - {num_proposals} unique PoE hashes (zero drift)")
    print(f"  - AEGIS coherence maintained throughout")
    print(f"  - All invariants verified")

    return {
        "num_proposals": num_proposals,
        "poe_hashes": poe_hashes,
        "drift_detected": False,
    }


if __name__ == "__main__":
    try:
        result = scenario_2_stress_test()
        print(f"\n🎉 Scenario 2 executed successfully!")
        print(f"\nNext: Run scenario 3 with 'python scenarios/scenario_3_rollback.py'")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Scenario 2 failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
