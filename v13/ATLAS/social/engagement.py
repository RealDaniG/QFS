"""
engagement.py - Deterministic Engagement & Sybil Resistance Logic

Implements the functions to weight engagement (comments, reactions)
and apply Sybil resistance costs (account age ramp-up).
"""

from v13.libs.BigNum128 import BigNum128


class EngagementCalculator:
    """
    Calculates engagement multipliers and sybil penalties.
    """

    def __init__(self):
        self.ZERO = BigNum128.from_int(0)
        self.ONE = BigNum128.from_int(1)
        self.TWO = BigNum128.from_int(2)
        self.HALF = BigNum128.from_string("0.5")

        # Sigmoid Parameters for Engagement Weight
        # Range: [0.5, 2.0]
        # Formula: Min + (Max - Min) * (x / (x + k))
        # k determines how fast it saturates.
        self.SIGMOID_K = BigNum128.from_int(
            50
        )  # Example: 50 quality points to reach half-saturation
        self.MIN_WEIGHT = self.HALF
        self.MAX_WEIGHT = self.TWO
        self.RANGE = self.MAX_WEIGHT.sub(self.MIN_WEIGHT)

    def compute_sybil_multiplier(
        self, account_age_epochs: int, ramp_epochs: int
    ) -> BigNum128:
        """
        Calculates the Sybil resistance multiplier [0.0, 1.0].
        multiplier = min(1.0, account_age / ramp_epochs)

        Args:
            account_age_epochs: Number of epochs user has been active
            ramp_epochs: Number of epochs to reach full reward eligibility
        """
        if ramp_epochs <= 0:
            return self.ONE

        if account_age_epochs >= ramp_epochs:
            return self.ONE

        age_bn = BigNum128.from_int(account_age_epochs)
        ramp_bn = BigNum128.from_int(ramp_epochs)

        return age_bn.div(ramp_bn)

    def compute_engagement_weight(self, sum_quality: BigNum128) -> BigNum128:
        """
        Calculates the engagement weight multiplier for a post.
        Uses algebraic sigmoid: 0.5 + 1.5 * (x / (x + 50))

        Args:
            sum_quality: Sum of quality scores of all comments (BigNum128)
        """
        if sum_quality < self.ZERO:  # Should be non-negative
            sum_quality = self.ZERO

        # x / (x + k)
        numerator = sum_quality
        denominator = sum_quality.add(self.SIGMOID_K)

        if denominator == self.ZERO:  # Should not happen if K > 0 and x >= 0
            fraction = self.ZERO
        else:
            fraction = numerator.div(denominator)

        # Min + Range * Fraction
        scaled_fraction = self.RANGE.mul(fraction)
        result = self.MIN_WEIGHT.add(scaled_fraction)

        return result
