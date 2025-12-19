"""
test_tier1_guarantees.py - Targeted verification for Tier 1 Governance hardening.

Verifies:
1. EconomicsGuard.validate_res_reward blocks over-draw conditions.
2. StateTransitionEngine ensures deterministic replay via sorted order.
"""

import pytest
from v13.libs.CertifiedMath import BigNum128, CertifiedMath
from v13.libs.economics.EconomicsGuard import EconomicsGuard, EconomicViolationType
from v13.libs.integration.StateTransitionEngine import StateTransitionEngine
from v13.core.TokenStateBundle import create_token_state_bundle


class TestTier1Guarantees:
    """Verification suite for hardened Tier 1 modules."""

    def test_resonance_draw_limit_violation(self):
        """Verify that RES rewards exceeding the draw limit are blocked."""
        cm = CertifiedMath()
        guard = EconomicsGuard(cm)

        # Total supply: 1M tokens
        total_supply = BigNum128.from_int(1_000_000)

        # Max draw is 5% (0.05) -> 50,000 tokens
        # Valid reward: 40,000 tokens
        valid_reward = BigNum128.from_int(40_000)
        result = guard.validate_res_reward(valid_reward, total_supply)
        assert result.passed is True

        # Invalid reward: 60,000 tokens
        invalid_reward = BigNum128.from_int(60_000)
        result = guard.validate_res_reward(invalid_reward, total_supply)
        assert result.passed is False
        assert result.error_code == EconomicViolationType.ECON_RES_REWARD_EXCEEDED.value
        assert "exceeds cap" in result.error_message

    def test_state_transition_deterministic_replay(self):
        """Verify that StateTransitionEngine produces identical hashes regardless of input order."""
        cm = CertifiedMath()
        engine = StateTransitionEngine(cm)

        # Initial bundle
        bundle = create_token_state_bundle(
            chr_state={"balance": "1000"},
            flx_state={"balance": "100"},
            psi_sync_state={"balance": "50"},
            atr_state={"balance": "500"},
            res_state={"balance": "20"},
            nod_state={
                "node_A": "100",
                "node_B": "100",
                "node_C": "100",
                "node_D": "100",
                "node_E": "100",
                "balance": "500",
            },
            lambda1=BigNum128.from_int(1),
            lambda2=BigNum128.from_int(1),
            c_crit=BigNum128.from_int(1),
            pqc_cid="pqc_1",
            timestamp=1000,
        )

        # Scenario 1: Allocations in order A, B
        allocations_1 = {
            "node_A": BigNum128.from_int(10),
            "node_B": BigNum128.from_int(20),
        }

        # Scenario 2: Allocations in order B, A (reverse)
        # Python 3.7+ dicts preserve insertion order, so we force difference
        allocations_2 = {}
        allocations_2["node_B"] = BigNum128.from_int(20)
        allocations_2["node_A"] = BigNum128.from_int(10)

        log_list_1 = []
        new_bundle_1 = engine.apply_state_transition(
            current_token_bundle=bundle,
            allocated_rewards={},
            nod_allocations=allocations_1,
            log_list=log_list_1,
            call_context="nod_allocation",
            deterministic_timestamp=2000,
        )

        log_list_2 = []
        new_bundle_2 = engine.apply_state_transition(
            current_token_bundle=bundle,
            allocated_rewards={},
            nod_allocations=allocations_2,
            log_list=log_list_2,
            call_context="nod_allocation",
            deterministic_timestamp=2000,
        )

        # Verify both produced identical hashes
        assert new_bundle_1.success is True
        assert new_bundle_2.success is True
        hash1 = new_bundle_1.new_token_bundle.get_deterministic_hash()
        hash2 = new_bundle_2.new_token_bundle.get_deterministic_hash()
        assert hash1 == hash2, (
            "State transitions must be deterministic regardless of input dictionary order"
        )


if __name__ == "__main__":
    pytest.main([__file__])
