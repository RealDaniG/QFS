"""
HSMF Math Contract Tests - Invariant and Bound Verification

Tests the mathematical contracts defined in docs/HSMF_MathContracts.md:
1. Action cost monotonicity (S_RES, S_FLX, λ₁)
2. C_holo bounds and inverse relationship to dissonance
3. Reward invariants (conservation, C_holo impact)
4. Determinism (bit-for-bit reproducibility)

NOTE: PQC is mocked in conftest.py because these invariants are independent of
the PQC crypto layer. HSMF math contracts are crypto-agnostic.
See: docs/HSMF_MathContracts.md#crypto-agnostic-math-layer
"""

import pytest

# Imports use v13.libs prefix consistently to avoid module identity mismatch.
# PQC mocks are registered in conftest.py before collection.
from v13.libs.BigNum128 import BigNum128
from v13.libs.CertifiedMath import CertifiedMath
from v13.core.HSMF import HSMF


class TestActionCostMonotonicity:
    """Test that action cost increases monotonically with inputs."""

    @pytest.fixture
    def hsmf(self):
        cm = CertifiedMath()
        return HSMF(cm)

    def test_action_cost_increases_with_s_res(self, hsmf):
        """Higher S_RES (resistance) should increase action cost."""
        log_list = []

        s_res_low = BigNum128.from_int(100)
        s_res_high = BigNum128.from_int(1000)
        s_flx = BigNum128.from_int(50)
        s_psi_sync = BigNum128.from_int(50)
        f_atr = BigNum128.from_int(10)
        lambda1 = BigNum128.from_int(1)
        lambda2 = BigNum128.from_int(1)

        cost_low = hsmf._calculate_action_cost_qfs(
            s_res_low, s_flx, s_psi_sync, f_atr, lambda1, lambda2, log_list, None
        )
        cost_high = hsmf._calculate_action_cost_qfs(
            s_res_high, s_flx, s_psi_sync, f_atr, lambda1, lambda2, log_list, None
        )

        assert cost_high.value > cost_low.value, (
            "Higher S_RES must increase action cost"
        )

    def test_action_cost_increases_with_s_flx(self, hsmf):
        """Higher S_FLX (flux deviation) should increase action cost."""
        log_list = []

        s_res = BigNum128.from_int(100)
        s_flx_low = BigNum128.from_int(50)
        s_flx_high = BigNum128.from_int(500)
        s_psi_sync = BigNum128.from_int(50)
        f_atr = BigNum128.from_int(10)
        lambda1 = BigNum128.from_int(1)
        lambda2 = BigNum128.from_int(1)

        cost_low = hsmf._calculate_action_cost_qfs(
            s_res, s_flx_low, s_psi_sync, f_atr, lambda1, lambda2, log_list, None
        )
        cost_high = hsmf._calculate_action_cost_qfs(
            s_res, s_flx_high, s_psi_sync, f_atr, lambda1, lambda2, log_list, None
        )

        assert cost_high.value > cost_low.value, (
            "Higher S_FLX must increase action cost"
        )

    def test_action_cost_increases_with_lambda1(self, hsmf):
        """Higher lambda1 (flux weight) should increase action cost when s_flx > 0."""
        log_list = []

        s_res = BigNum128.from_int(100)
        s_flx = BigNum128.from_int(100)  # Non-zero flux
        s_psi_sync = BigNum128.from_int(50)
        f_atr = BigNum128.from_int(10)
        lambda1_low = BigNum128.from_int(1)
        lambda1_high = BigNum128.from_int(10)
        lambda2 = BigNum128.from_int(1)

        cost_low = hsmf._calculate_action_cost_qfs(
            s_res, s_flx, s_psi_sync, f_atr, lambda1_low, lambda2, log_list, None
        )
        cost_high = hsmf._calculate_action_cost_qfs(
            s_res, s_flx, s_psi_sync, f_atr, lambda1_high, lambda2, log_list, None
        )

        assert cost_high.value > cost_low.value, (
            "Higher lambda1 must increase action cost"
        )


class TestCoherenceInvariants:
    """Test C_holo (holistic coefficient) invariants."""

    @pytest.fixture
    def hsmf(self):
        cm = CertifiedMath()
        return HSMF(cm)

    def test_c_holo_bounded_zero_to_one(self, hsmf):
        """C_holo must be in range (0, 1]."""
        log_list = []

        # Zero dissonance -> C_holo = 1
        c_holo_perfect = hsmf._calculate_c_holo(
            BigNum128.from_int(0),
            BigNum128.from_int(0),
            BigNum128.from_int(0),
            log_list,
            None,
        )

        # High dissonance -> C_holo approaches 0
        c_holo_bad = hsmf._calculate_c_holo(
            BigNum128.from_int(1000000),
            BigNum128.from_int(1000000),
            BigNum128.from_int(1000000),
            log_list,
            None,
        )

        one = BigNum128.from_int(1)
        zero = BigNum128.from_int(0)

        # C_holo at zero dissonance should equal 1
        assert c_holo_perfect.value == one.value, (
            "Zero dissonance must yield C_holo = 1"
        )

        # C_holo at high dissonance should be < 1
        assert c_holo_bad.value < one.value, "High dissonance must reduce C_holo"
        assert c_holo_bad.value > zero.value, "C_holo must remain positive"

    def test_c_holo_decreases_with_dissonance(self, hsmf):
        """Higher dissonance must decrease C_holo (inverse relationship)."""
        log_list = []

        c_holo_low = hsmf._calculate_c_holo(
            BigNum128.from_int(10),
            BigNum128.from_int(10),
            BigNum128.from_int(10),
            log_list,
            None,
        )
        c_holo_high = hsmf._calculate_c_holo(
            BigNum128.from_int(100),
            BigNum128.from_int(100),
            BigNum128.from_int(100),
            log_list,
            None,
        )

        assert c_holo_low.value > c_holo_high.value, (
            "Lower dissonance must yield higher C_holo"
        )


class TestRewardWeightInvariants:
    """Test reward computation invariants."""

    @pytest.fixture
    def hsmf(self):
        cm = CertifiedMath()
        return HSMF(cm)

    def test_higher_c_holo_increases_chr_reward(self, hsmf):
        """Higher C_holo should increase CHR reward."""
        log_list = []

        # Same S_CHR, different C_holo
        metrics_low_coherence = {
            "s_chr": BigNum128.from_int(100),
            "c_holo": BigNum128.from_int(500),  # 0.5 scaled
            "s_res": BigNum128.from_int(10),
            "s_flx": BigNum128.from_int(10),
            "s_psi_sync": BigNum128.from_int(10),
            "f_atr": BigNum128.from_int(10),
            "action_cost": BigNum128.from_int(100),
        }
        metrics_high_coherence = {
            "s_chr": BigNum128.from_int(100),
            "c_holo": BigNum128.from_int(900),  # 0.9 scaled
            "s_res": BigNum128.from_int(10),
            "s_flx": BigNum128.from_int(10),
            "s_psi_sync": BigNum128.from_int(10),
            "f_atr": BigNum128.from_int(10),
            "action_cost": BigNum128.from_int(100),
        }

        rewards_low = hsmf._compute_hsmf_rewards(metrics_low_coherence, log_list)
        rewards_high = hsmf._compute_hsmf_rewards(metrics_high_coherence, log_list)

        assert rewards_high["chr_reward"].value > rewards_low["chr_reward"].value, (
            "Higher C_holo must increase CHR reward"
        )

    def test_total_reward_is_sum_of_parts(self, hsmf):
        """Total reward must equal sum of individual token rewards."""
        log_list = []

        metrics = {
            "s_chr": BigNum128.from_int(100),
            "c_holo": BigNum128.from_int(800),
            "s_res": BigNum128.from_int(20),
            "s_flx": BigNum128.from_int(30),
            "s_psi_sync": BigNum128.from_int(15),
            "f_atr": BigNum128.from_int(25),
            "action_cost": BigNum128.from_int(150),
        }

        rewards = hsmf._compute_hsmf_rewards(metrics, log_list)

        expected_total = (
            rewards["chr_reward"].value
            + rewards["flx_reward"].value
            + rewards["res_reward"].value
            + rewards["psi_sync_reward"].value
            + rewards["atr_reward"].value
        )

        assert rewards["total_reward"].value == expected_total, (
            "Total reward must equal sum of individual rewards"
        )


class TestDeterminism:
    """Test that HSMF computations are deterministic."""

    @pytest.fixture
    def hsmf(self):
        cm = CertifiedMath()
        return HSMF(cm)

    def test_action_cost_deterministic(self, hsmf):
        """Same inputs must produce identical action cost."""
        log_list_1 = []
        log_list_2 = []

        s_res = BigNum128.from_int(100)
        s_flx = BigNum128.from_int(50)
        s_psi_sync = BigNum128.from_int(75)
        f_atr = BigNum128.from_int(25)
        lambda1 = BigNum128.from_int(2)
        lambda2 = BigNum128.from_int(3)

        cost_1 = hsmf._calculate_action_cost_qfs(
            s_res, s_flx, s_psi_sync, f_atr, lambda1, lambda2, log_list_1, None
        )
        cost_2 = hsmf._calculate_action_cost_qfs(
            s_res, s_flx, s_psi_sync, f_atr, lambda1, lambda2, log_list_2, None
        )

        assert cost_1.value == cost_2.value, (
            "Identical inputs must yield identical outputs"
        )

    def test_c_holo_deterministic(self, hsmf):
        """Same inputs must produce identical C_holo."""
        log_list_1 = []
        log_list_2 = []

        s_res = BigNum128.from_int(100)
        s_flx = BigNum128.from_int(50)
        s_psi_sync = BigNum128.from_int(75)

        c_holo_1 = hsmf._calculate_c_holo(s_res, s_flx, s_psi_sync, log_list_1, None)
        c_holo_2 = hsmf._calculate_c_holo(s_res, s_flx, s_psi_sync, log_list_2, None)

        assert c_holo_1.value == c_holo_2.value, (
            "Identical inputs must yield identical C_holo"
        )


class TestEdgeCases:
    """Test edge cases: minimal values, high values, boundary conditions."""

    @pytest.fixture
    def hsmf(self):
        cm = CertifiedMath()
        return HSMF(cm)

    def test_action_cost_with_minimal_inputs(self, hsmf):
        """Near-zero activity should produce minimal action cost."""
        log_list = []

        # Minimal non-zero inputs (equivalent to 0.000001 in scaled terms)
        minimal = BigNum128.from_int(1)  # 1 * SCALE = very small
        zero = BigNum128.from_int(0)

        cost = hsmf._calculate_action_cost_qfs(
            minimal,
            minimal,
            minimal,
            zero,
            BigNum128.from_int(1),
            BigNum128.from_int(1),
            log_list,
            None,
        )

        # Cost should be positive and small
        assert cost.value > 0, "Minimal inputs should still produce positive cost"
        # Cost should be roughly 3 * minimal (s_res + λ₁*s_flx + λ₂*s_psi_sync)
        expected_approx = minimal.value * 3
        assert cost.value <= expected_approx * 2, (
            "Cost should be bounded at minimal inputs"
        )

    def test_action_cost_with_high_inputs(self, hsmf):
        """High (but safe) inputs should not overflow."""
        log_list = []

        # High values within safe bounds (10^9 scaled)
        high = BigNum128.from_int(10**9)
        lambda_high = BigNum128.from_int(100)

        # Should not raise OverflowError
        cost = hsmf._calculate_action_cost_qfs(
            high, high, high, high, lambda_high, lambda_high, log_list, None
        )

        # Cost should be positive and larger than any single input
        assert cost.value > high.value, "High dissonance should produce high cost"

    def test_c_holo_at_minimal_dissonance(self, hsmf):
        """Near-zero dissonance should yield C_holo ≈ 1."""
        log_list = []

        # Very small dissonance: 0.001 each in BigNum128 terms
        # BigNum128 SCALE = 10^18, so 0.001 = 10^15 raw
        tiny = BigNum128(10**15)  # 0.001 in fixed-point

        c_holo = hsmf._calculate_c_holo(tiny, tiny, tiny, log_list, None)
        one = BigNum128.from_int(1)

        # C_holo should be very close to 1 (slightly less due to tiny dissonance)
        assert c_holo.value < one.value, "Some dissonance must reduce C_holo"
        # With total_dissonance = 0.003, c_holo = 1/(1+0.003) ≈ 0.997
        # Should be at least 99% of 1 given tiny dissonance
        assert c_holo.value > (one.value * 99) // 100, (
            "Tiny dissonance should barely affect C_holo"
        )

    def test_c_holo_at_high_dissonance(self, hsmf):
        """Very high dissonance should yield C_holo approaching 0."""
        log_list = []

        # Very high dissonance
        huge = BigNum128.from_int(10**12)

        c_holo = hsmf._calculate_c_holo(huge, huge, huge, log_list, None)
        one = BigNum128.from_int(1)

        # C_holo should be extremely small (close to 0)
        assert c_holo.value > 0, "C_holo must remain positive"
        assert c_holo.value < one.value // 1000, (
            "Huge dissonance should yield C_holo < 0.001"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
