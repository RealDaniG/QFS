"""
growth.py - Deterministic Growth Dynamics for Social Emissions

Implements the feedback loop where system-wide coherence drives
the growth (or contraction) of the Social Flux Emission Pool.
"""

from v13.libs.BigNum128 import BigNum128


class GrowthEngine:
    """
    Calculates the emission pool for the NEXT epoch based on performance of
    the CURRENT epoch.
    """

    def __init__(self):
        self.ZERO = BigNum128.from_int(0)
        self.ONE = BigNum128.from_int(1)

        # Baselines
        self.BASE_COHERENCE_TARGET = BigNum128.from_string(
            "0.70"
        )  # Expect 70% coherence

        # Caps
        self.MAX_MULTIPLIER = BigNum128.from_string(
            "1.5"
        )  # Max 50% growth per epoch step relative to base?
        # Actually usually relative to BASE emission, not compounding infinitely strictly.
        # "SocialEmission(E+1) = BaseSocialEmission * g(GlobalCoherence(E))"
        # So we store a Static Base and apply a dynamic multiplier.

        self.MIN_MULTIPLIER = BigNum128.from_string("0.5")

        # Sensitivity
        self.GROWTH_SLOPE = BigNum128.from_string("1.0")  # 1:1 response

    def calculate_next_emission(
        self, base_emission: BigNum128, avg_epoch_coherence: BigNum128
    ) -> BigNum128:
        """
        Compute SocialEmission(E+1).
        Formula: Base * Clamp(1 + Slope * (AvgCoh - Target), Min, Max)
        """

        # 1. Delta = Avg - Target
        # if Avg < Target, Delta is negative.
        # BigNum128 might not handle negative directly if unsigned?
        # Usually BigNum128 is signed in QFS implementation?
        # If not, we handle cases.

        multiplier = self.ONE

        if avg_epoch_coherence > self.BASE_COHERENCE_TARGET:
            # Growth
            delta = avg_epoch_coherence.sub(self.BASE_COHERENCE_TARGET)
            boost = delta.mul(self.GROWTH_SLOPE)
            multiplier = self.ONE.add(boost)
        else:
            # Decay
            delta = self.BASE_COHERENCE_TARGET.sub(avg_epoch_coherence)
            penalty = delta.mul(self.GROWTH_SLOPE)
            if penalty > self.ONE:  # Should not happen if target is 0.7
                multiplier = self.ZERO  # Cap at 0
            else:
                multiplier = self.ONE.sub(penalty)

        # 2. Clamp Multiplier
        if multiplier > self.MAX_MULTIPLIER:
            multiplier = self.MAX_MULTIPLIER
        elif multiplier < self.MIN_MULTIPLIER:
            multiplier = self.MIN_MULTIPLIER

        # 3. Calculate Result
        return base_emission.mul(multiplier)
