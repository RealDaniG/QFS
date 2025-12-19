"""
Testnet Scenario 3: Emergency Rollback
Goal: Rollback to previous parameter snapshot after a change
Expected Outcome: Parameters restored to snapshot, invariants preserved
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


def scenario_3_rollback():
    """Execute Scenario 3: Emergency Rollback."""

    print("=" * 80)
    print("Testnet Scenario 3: Emergency Rollback")
    print("Goal: Rollback to previous parameter snapshot")
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

    # Step 1: Create snapshot of current parameters
    print("\n[STEP 1/5] Creating parameter snapshot...")
    snapshot = {}
    for key in registry.get_all_parameters().keys():
        snapshot[key] = registry.get(key)
    print(f"✓ Snapshot created with {len(snapshot)} parameters")

    # Step 2: Execute a parameter change
    print("\n[STEP 2/5] Executing parameter change...")
    original_value = registry.get("VIRAL_POOL_CAP")
    new_value = BigNum128(2_000_000_000_000_000_000_000_000_000)  # 2B CHR

    proposal = engine.create_proposal(
        kind="PARAMETER_CHANGE",
        title="Test Parameter Change",
        description="Change VIRAL_POOL_CAP to 2B for rollback test",
        parameter_key="VIRAL_POOL_CAP",
        new_value=new_value,
        proposer_wallet="wallet_rollback_test",
    )

    engine.vote(proposal.proposal_id, "wallet_rollback_test", True, stake=1000)
    engine.execute_proposal(proposal.proposal_id)

    changed_value = registry.get("VIRAL_POOL_CAP")
    assert changed_value == new_value, "Parameter change failed"
    print(
        f"✓ Parameter changed: {int(original_value) // 10**18:,} → {int(changed_value) // 10**18:,} CHR"
    )

    # Step 3: Verify AEGIS coherence after change
    print("\n[STEP 3/5] Verifying AEGIS coherence after change...")
    is_coherent, msg = aegis.verify_coherence()
    assert is_coherent, f"AEGIS coherence failed after change: {msg}"
    print(f"✓ AEGIS Status: COHERENT")

    # Step 4: Execute rollback
    print("\n[STEP 4/5] Executing rollback to snapshot...")

    # Create rollback proposal
    rollback_proposal = engine.create_proposal(
        kind="PARAMETER_CHANGE",
        title="Emergency Rollback",
        description="Rollback VIRAL_POOL_CAP to snapshot value",
        parameter_key="VIRAL_POOL_CAP",
        new_value=snapshot["VIRAL_POOL_CAP"],
        proposer_wallet="wallet_rollback_admin",
    )

    engine.vote(
        rollback_proposal.proposal_id, "wallet_rollback_admin", True, stake=1000
    )
    engine.execute_proposal(rollback_proposal.proposal_id)

    rolled_back_value = registry.get("VIRAL_POOL_CAP")
    print(
        f"✓ Rollback executed: {int(changed_value) // 10**18:,} → {int(rolled_back_value) // 10**18:,} CHR"
    )

    # Step 5: Verify rollback success
    print("\n[STEP 5/5] Verifying rollback success...")

    # Check parameter matches snapshot
    assert rolled_back_value == snapshot["VIRAL_POOL_CAP"], (
        "Rollback failed: value mismatch"
    )
    print(f"✓ Parameter matches snapshot")

    # Verify AEGIS coherence after rollback
    is_coherent, msg = aegis.verify_coherence()
    assert is_coherent, f"AEGIS coherence failed after rollback: {msg}"
    print(f"✓ Final AEGIS Status: COHERENT - {msg}")

    # Verify all other parameters unchanged
    for key, value in snapshot.items():
        if key != "VIRAL_POOL_CAP":  # We changed this one
            current_value = registry.get(key)
            assert current_value == value, f"Parameter {key} unexpectedly changed"
    print(f"✓ All other parameters unchanged")

    print("\n" + "=" * 80)
    print("Scenario 3: COMPLETE ✓")
    print("=" * 80)

    print("\n✅ All checks passed:")
    print("  - Snapshot created successfully")
    print("  - Parameter change executed")
    print("  - Rollback executed successfully")
    print("  - Parameter restored to snapshot value")
    print("  - AEGIS coherence maintained throughout")
    print("  - All other parameters unchanged")

    return {
        "snapshot_size": len(snapshot),
        "rollback_successful": True,
        "parameter_restored": rolled_back_value == snapshot["VIRAL_POOL_CAP"],
    }


if __name__ == "__main__":
    try:
        result = scenario_3_rollback()
        print(f"\n🎉 Scenario 3 executed successfully!")
        print(
            f"\nNext: Run scenario 4 with 'python scenarios/scenario_4_reward_multiplier.py'"
        )
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Scenario 3 failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
