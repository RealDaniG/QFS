"""
Deterministic Mathematical Constants for AES
All values scaled to avoid floating-point drift.
"""
PHI = 1618033989
PHI_INV = 618033989
PHI_SQ = 2618033988
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]
GOLDEN_ANGLE = 137507764
HEX_ANGLE = 60000000
TRIANGLE_ANGLE = 120000000
SCALE = 10 ** 9

def phi_ratio(a: int, b: int) -> int:
    """
    Check if ratio a/b aligns with φ within tolerance.
    Returns deviation score (0 = perfect alignment, higher = worse).
    """
    ratio = a * SCALE // b if b != 0 else 0
    deviation = abs(ratio - PHI)
    return deviation
