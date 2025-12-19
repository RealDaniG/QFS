"""
Testnet Scenario 1: Change Emission Cap
Goal: Increase VIRAL_POOL_CAP from 1B to 1.5B CHR
Expected Outcome: Parameter updated, AEGIS coherent, PoE artifact generated
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


def scenario_1_change_emission_cap():
    """Execute Scenario 1: Change Emission Cap."""

    print("=" * 80)
    print("Testnet Scenario 1: Change Emission Cap")
    print("Goal: Increase VIRAL_POOL_CAP from 1B to 1.5B CHR")
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

    # Get initial value
    initial_value = registry.get("VIRAL_POOL_CAP")
    print(f"✓ Initial VIRAL_POOL_CAP: {int(initial_value) // 10**18:,} CHR")

    # Step 1: Create proposal
    print("\n[STEP 1/5] Creating proposal...")
    proposal = engine.create_proposal(
        kind="PARAMETER_CHANGE",
        title="Increase Viral Pool Cap",
        description="Increase VIRAL_POOL_CAP from 1B to 1.5B CHR to support growing user base",
        parameter_key="VIRAL_POOL_CAP",
        new_value=BigNum128(1_500_000_000_000_000_000_000_000_000),
        proposer_wallet="wallet_scenario_1",
    )

    print(f"✓ Proposal created")
    print(f"  - Proposal ID: {proposal.proposal_id}")
    print(f"  - Title: {proposal.title}")
    print(f"  - Parameter: {proposal.parameter_key}")
    print(f"  - New Value: 1,500,000,000 CHR")

    # Step 2: Vote
    print("\n[STEP 2/5] Voting on proposal...")
    engine.vote(proposal.proposal_id, "wallet_scenario_1", True, stake=1000)
    print(f"✓ Vote cast: YES with 1000 stake")

    # Step 3: Check if passed
    print("\n[STEP 3/5] Checking proposal status...")
    passed = engine.check_passed(proposal.proposal_id)
    assert passed, "Proposal should pass with >66% supermajority"
    print("✓ Proposal PASSED (>66% supermajority)")

    # Step 4: Execute
    print("\n[STEP 4/5] Executing proposal...")
    engine.execute_proposal(proposal.proposal_id)
    print("✓ Proposal executed")

    # Verify parameter change
    new_value = registry.get("VIRAL_POOL_CAP")
    expected_value = BigNum128(1_500_000_000_000_000_000_000_000_000)
    assert new_value == expected_value, (
        f"Parameter not updated correctly: {new_value} != {expected_value}"
    )
    print(f"✓ Parameter updated: {int(new_value) // 10**18:,} CHR")

    # Step 5: Verify AEGIS coherence
    print("\n[STEP 5/5] Verifying AEGIS coherence...")
    is_coherent, msg = aegis.verify_coherence()
    assert is_coherent, f"Post-execution AEGIS check failed: {msg}"
    print(f"✓ Final AEGIS Status: COHERENT - {msg}")

    # Generate PoE artifact
    poe_hash = engine.get_execution_proof(proposal.proposal_id)
    print(f"\n📜 Proof-of-Execution:")
    print(f"  - Proposal ID: {proposal.proposal_id}")
    print(f"  - PoE Hash: {poe_hash}")
    print(f"  - Parameter: VIRAL_POOL_CAP")
    print(f"  - Old Value: 1,000,000,000 CHR")
    print(f"  - New Value: 1,500,000,000 CHR")

    print("\n" + "=" * 80)
    print("Scenario 1: COMPLETE ✓")
    print("=" * 80)

    print("\n✅ All checks passed:")
    print("  - Proposal created and voted on")
    print("  - Supermajority achieved")
    print("  - Proposal executed successfully")
    print("  - Parameter updated correctly")
    print("  - AEGIS coherence maintained")
    print("  - PoE artifact generated")

    return {
        "proposal_id": proposal.proposal_id,
        "poe_hash": poe_hash,
        "old_value": int(initial_value) // 10**18,
        "new_value": int(new_value) // 10**18,
    }


if __name__ == "__main__":
    try:
        result = scenario_1_change_emission_cap()
        print(f"\n🎉 Scenario 1 executed successfully!")
        print(
            f"\nNext: Run scenario 2 with 'python scenarios/scenario_2_stress_test.py'"
        )
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Scenario 1 failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
