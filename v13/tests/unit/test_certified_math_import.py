import sys
import unittest

# Ensure v13 root is in path
sys.path.append(".")

from v13.libs.CertifiedMath import CertifiedMath, get_PI
from v13.libs.BigNum128 import BigNum128


class TestCertifiedMathSmoke(unittest.TestCase):
    """
    Smoke tests to ensure CertifiedMath remains importable and conflict-free.
    """

    def test_import_and_basic_op(self):
        # 1. Verify Import (Implicit by reaching here)
        print("\n[Smoke] CertifiedMath imported successfully.")

        # 2. Verify Basic Ops
        a = BigNum128.from_int(100)
        b = BigNum128.from_int(200)

        # Test safe add
        res_add = CertifiedMath._safe_add(a, b, [], None, None)
        self.assertEqual(res_add.value, 300 * BigNum128.SCALE)
        print("[Smoke] _safe_add verified.")

        # Test safe mul
        res_mul = CertifiedMath._safe_mul(a, b, [], None, None)
        # Expected: 20000 * SCALE
        expected_mul = 20000 * BigNum128.SCALE
        self.assertEqual(res_mul.value, expected_mul)
        print(f"[Smoke] _safe_mul verified: {res_mul.value}")

        # 3. Verify System Constants usage
        # This checks that get_PI/get_LN10 etc are accessible
        pi = get_PI()
        self.assertIsNotNone(pi)
        print("[Smoke] System constants accessible.")


if __name__ == "__main__":
    unittest.main()
