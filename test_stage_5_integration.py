"""
test_stage_5_integration.py - Verify End-to-End Autonomous Governance Flow

Invariants:
- Proposal Execution updates Registry (GOV-I1).
- Binder sees Updated Value (ECON-I1 check).
- Immutable parameters remain protected.
"""

from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128
from v13.libs.governance.RewardAllocator import RewardAllocator
from v13.policy.governance.GovernanceParameterRegistry import (
    GovernanceParameterRegistry,
)
from v13.policy.governance.ProposalEngine import ProposalEngine
from v13.atlas.economics.ViralRewardBinder import ViralRewardBinder


def test_governance_feedback_loop():
    print("Starting Stage 5 Integration Test...")

    # 1. Setup Infrastructure
    cm = CertifiedMath()
    allocator = RewardAllocator(cm)
    registry = GovernanceParameterRegistry()
    proposal_engine = ProposalEngine()

    binder = ViralRewardBinder(cm, allocator, registry=registry)

    # 2. Verify Initial State (Default Cap)
    initial_cap = binder.VIRAL_POOL_CAP
    print(f"Initial Cap: {initial_cap.to_decimal_string()}")
    assert initial_cap == BigNum128.from_int(1_000_000)  # Default

    # 3. Create Proposal to Lower Cap to 500,000
    new_cap_val = 500_000
    payload = {
        "action": "PARAMETER_CHANGE",
        "key": "VIRAL_POOL_CAP",
        "value": new_cap_val,
    }

    prop_id = proposal_engine.create_proposal(
        title="Reduce Viral Cap",
        description="Lowers cap to half for stability.",
        execution_payload=payload,
    )

    # 4. Execute Proposal (Simulates Voting Pass)
    success = proposal_engine.execute_proposal(prop_id, registry)
    assert success is True
    print("Proposal Executed Successfully.")

    # 5. Verify Binder Sees New Value
    current_cap = binder.VIRAL_POOL_CAP
    print(f"New Cap: {current_cap.to_decimal_string()}")
    assert current_cap == BigNum128.from_int(new_cap_val)

    # 6. Verify Protection (Attempt to change immutable)
    # Assuming CHR_DAILY_EMISSION_CAP is immutable (not in MUTABLE_KEYS)
    immutable_payload = {
        "action": "PARAMETER_CHANGE",
        "key": "CHR_DAILY_EMISSION_CAP",
        "value": 20_000_000,
    }
    bad_prop_id = proposal_engine.create_proposal("Bad Prop", "Desc", immutable_payload)
    success_bad = proposal_engine.execute_proposal(bad_prop_id, registry)

    assert success_bad is False
    print("Immutable Parameter Protection Verified.")

    print("Stage 5 Integration Test PASSED: Self-Amendment Cycle Confirmed.")


if __name__ == "__main__":
    test_governance_feedback_loop()
