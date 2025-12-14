"""
Deterministic Mathematical Constants for AES
All values scaled to avoid floating-point drift.
"""

# Golden Ratio (φ) scaled to 10^9 for precision
PHI = 1618033989  # φ ≈ 1.618033989
PHI_INV = 618033989  # 1/φ ≈ 0.618033989
PHI_SQ = 2618033988  # φ² ≈ 2.618033988

# Fibonacci sequence (first 20 terms for reference)
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]

# Sacred Geometry Angles (degrees * 10^6)
GOLDEN_ANGLE = 137507764  # 360 / φ² ≈ 137.507764°
HEX_ANGLE = 60000000  # 60° for hexagonal symmetry
TRIANGLE_ANGLE = 120000000  # 120° for triangular patterns

# Scaling factor for all computations
SCALE = 10**9

def phi_ratio(a: int, b: int) -> int:
    """
    Check if ratio a/b aligns with φ within tolerance.
    Returns deviation score (0 = perfect alignment, higher = worse).
    """
    ratio = (a * SCALE) // b if b != 0 else 0
    deviation = abs(ratio - PHI)
    return deviation
