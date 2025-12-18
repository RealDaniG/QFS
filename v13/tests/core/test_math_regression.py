"""
Math Core Regression Suite
Locks in the exact behavior of CertifiedMath and BigNum128.
Replays a deterministic sequence of operations to ensure no drift in precision or rounding.
"""

import pytest
import pytest
import hashlib
import sys
import os

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.BigNum128 import BigNum128
except ImportError:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    )
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.BigNum128 import BigNum128


def generate_op_sequence(seed: str, count: int):
    """Deterministic PRNG for test vector generation."""
    state = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    for _ in range(count):
        # Linear Congruential Generator
        state = (state * 1664525 + 1013904223) % (2**64)
        yield state


def test_math_regression_baseline():
    """
    Run 1000 operations of mixed types and verify the final accumulated state hash.
    If this hash changes, IT IS A BREAKING CHANGE to the economy.
    """
    cm = CertifiedMath()
    accumulator = BigNum128(0)

    # Generate deterministic inputs
    # We map random u64s to BigNum inputs
    inputs = list(generate_op_sequence("v13.9-baseline", 1000))

    current_hash = ""

    for i, val in enumerate(inputs):
        op_type = i % 4

        # Create a deterministic operand (fit within reasonable range)
        operand_val = val % (10**24)  # ~ 1 million tokens with 18 decimals
        operand = BigNum128(operand_val)

        if accumulator.value > BigNum128.MAX_VALUE // 2:
            op_type = 3  # Force DIV if getting too big
        elif accumulator.value < BigNum128.SCALE:
            op_type = 0  # Force ADD if getting too small

        if op_type == 0:  # ADD
            accumulator = cm.add(accumulator, operand)
        elif op_type == 1:  # SUB
            if accumulator.value > operand.value:
                accumulator = cm.sub(accumulator, operand)
            else:
                accumulator = cm.add(accumulator, operand)
        elif op_type == 2:  # MUL (Scaled)
            # Range [0.5, 1.5] roughly to prevent explosion
            # val % 10**18 is [0, 1.0]. Plus 0.5*10**18 = [0.5, 1.5]
            # Actually just keep it simple: val % 1.5 * 10**18
            raw_mult = val % (15 * 10**17)
            multiplier = BigNum128(raw_mult)
            accumulator = cm.mul(accumulator, multiplier)
        elif op_type == 3:  # DIV
            # divisor must be non-zero
            divisor_val = (val % (10**18)) + (10**17)  # at least 0.1
            divisor = BigNum128(divisor_val)
            accumulator = cm.div(accumulator, divisor)

    # Final Verification
    final_int = accumulator.value
    final_hash = hashlib.sha256(str(final_int).encode()).hexdigest()

    # print(f"DEBUG: Final Int: {final_int}")
    # print(f"DEBUG: Final Hash: {final_hash}")

    # EXPECTED HASH for V13.9 Logic
    # Note: I am first running this to capture the hash, then I will hardcode it.
    # For this first run, I will assert checks on sanity, but I need to 'lock' the hash.
    # So I will assert True first, capture the output, then update this file.

    # v13.9 Baseline Hash (Locked 2025-12-18)
    BASELINE_HASH = "5b97c505bee1a7e247bdc6abd89728d9485e7f8e398029db83009657512f78a9"

    # If this assertion fails, you have broken the economic math core.
    # Do NOT update this hash unless strictly authorized by the Math Stewardship rules.
    assert final_hash == BASELINE_HASH, (
        f"Math Core Regression! Expected {BASELINE_HASH}, got {final_hash}"
    )
    print(f"BASELINE_HASH:{final_hash} (VERIFIED)")


if __name__ == "__main__":
    test_math_regression_baseline()
