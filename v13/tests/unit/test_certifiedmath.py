"""
CertifiedMath Test Suite

This test suite verifies that the CertifiedMath implementation is working correctly
and adheres to the Zero-Simulation mandate.

Tests include:
- Basic arithmetic operations
- Edge cases and boundary conditions
- Deterministic behavior across multiple runs
- Audit logging functionality
"""

from v13.libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    qnum,
)
import json
from v13.libs.CertifiedMath import CertifiedMath, BigNum128


class CertifiedMathTest:
    """Test suite for CertifiedMath implementation."""

    def __init__(self):
        self.log_list = []
        self.certified_math = CertifiedMath(self.log_list)
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def run_tests(self):
        """Run all tests."""
        print("Running CertifiedMath Test Suite...")
        print("=" * 50)
        self.test_basic_arithmetic()
        self.test_edge_cases()
        self.test_deterministic_behavior()
        self.test_audit_logging()
        self.test_comparison_operations()
        self.test_rounding_operations()
        print("=" * 50)
        print(f"Tests passed: {self.passed}")
        print(f"Tests failed: {self.failed}")
        print(f"Total tests: {self.passed + self.failed}")
        self.generate_report()
        return self.failed == 0

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        print("Testing basic arithmetic operations...")
        a = BigNum128.from_string("1.0")
        b = BigNum128.from_string("2.0")
        result = self.certified_math.add(a, b, pqc_cid="TEST_ADD")
        expected = BigNum128.from_string("3.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Addition test passed")
            self.passed += 1
        else:
            print(
                f"  ❌ Addition test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}"
            )
            self.failed += 1
            self.test_results.append(
                {
                    "test": "basic_arithmetic_addition",
                    "status": "FAILED",
                    "expected": expected.to_decimal_string(),
                    "actual": result.to_decimal_string(),
                }
            )
        a = BigNum128.from_string("3.0")
        b = BigNum128.from_string("1.0")
        result = self.certified_math.sub(a, b, pqc_cid="TEST_SUB")
        expected = BigNum128.from_string("2.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Subtraction test passed")
            self.passed += 1
        else:
            print(
                f"  ❌ Subtraction test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}"
            )
            self.failed += 1
            self.test_results.append(
                {
                    "test": "basic_arithmetic_subtraction",
                    "status": "FAILED",
                    "expected": expected.to_decimal_string(),
                    "actual": result.to_decimal_string(),
                }
            )
        a = BigNum128.from_string("2.0")
        b = BigNum128.from_string("3.0")
        result = self.certified_math.mul(a, b, pqc_cid="TEST_MUL")
        expected = BigNum128.from_string("6.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Multiplication test passed")
            self.passed += 1
        else:
            print(
                f"  ❌ Multiplication test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}"
            )
            self.failed += 1
            self.test_results.append(
                {
                    "test": "basic_arithmetic_multiplication",
                    "status": "FAILED",
                    "expected": expected.to_decimal_string(),
                    "actual": result.to_decimal_string(),
                }
            )
        a = BigNum128.from_string("6.0")
        b = BigNum128.from_string("2.0")
        result = self.certified_math.div(a, b, pqc_cid="TEST_DIV")
        expected = BigNum128.from_string("3.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Division test passed")
            self.passed += 1
        else:
            print(
                f"  ❌ Division test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}"
            )
            self.failed += 1
            self.test_results.append(
                {
                    "test": "basic_arithmetic_division",
                    "status": "FAILED",
                    "expected": expected.to_decimal_string(),
                    "actual": result.to_decimal_string(),
                }
            )

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("Testing edge cases...")
        a = BigNum128.from_string("0.0")
        b = BigNum128.from_string("1.0")
        result = self.certified_math.add(a, b, pqc_cid="TEST_ZERO_ADD")
        expected = BigNum128.from_string("1.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Zero addition test passed")
            self.passed += 1
        else:
            print(
                f"  ❌ Zero addition test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}"
            )
            self.failed += 1
        a = BigNum128.from_string("-1.0")
        b = BigNum128.from_string("2.0")
        result = self.certified_math.add(a, b, pqc_cid="TEST_NEG_ADD")
        expected = BigNum128.from_string("1.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Negative number test passed")
            self.passed += 1
        else:
            print(
                f"  ❌ Negative number test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}"
            )
            self.failed += 1

    def test_deterministic_behavior(self):
        """Test that operations are deterministic across multiple runs."""
        print("Testing deterministic behavior...")
        results = []
        a = BigNum128.from_string("1.23456789")
        b = BigNum128.from_string("9.87654321")
        for i in range(5):
            log_list = []
            cm = CertifiedMath(log_list)
            result = cm.add(a, b, pqc_cid=f"TEST_DET_{i}")
            results.append(result.value)
        if all((r == results[0] for r in results)):
            print("  ✅ Deterministic behavior test passed")
            self.passed += 1
        else:
            print(f"  ❌ Deterministic behavior test failed: results vary ({results})")
            self.failed += 1

    def test_audit_logging(self):
        """Test audit logging functionality."""
        print("Testing audit logging...")
        log_list = []
        cm = CertifiedMath(log_list)
        a = BigNum128.from_string("1.0")
        b = BigNum128.from_string("2.0")
        result = cm.add(a, b, pqc_cid="TEST_LOG")
        if len(log_list) > 0:
            print("  ✅ Audit logging test passed")
            self.passed += 1
        else:
            print("  ❌ Audit logging test failed: no audit entries found")
            self.failed += 1

    def test_comparison_operations(self):
        """Test comparison operations."""
        print("Testing comparison operations...")
        a = BigNum128.from_string("2.0")
        b = BigNum128.from_string("1.0")
        if a.value > b.value:
            print("  ✅ Greater than test passed")
            self.passed += 1
        else:
            print("  ❌ Greater than test failed")
            self.failed += 1
        a = BigNum128.from_string("1.0")
        b = BigNum128.from_string("2.0")
        if a.value < b.value:
            print("  ✅ Less than test passed")
            self.passed += 1
        else:
            print("  ❌ Less than test failed")
            self.failed += 1

    def test_rounding_operations(self):
        """Test rounding operations."""
        print("Testing rounding operations...")
        try:
            a = BigNum128.from_string("1.5")
            print("  ⚠️  Floor method test skipped (not implemented in BigNum128)")
        except AttributeError:
            print("  ⚠️  Floor method not implemented, skipping test")

    def generate_report(self):
        """Generate a test report."""
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tests_run": self.passed + self.failed,
            "tests_passed": self.passed,
            "tests_failed": self.failed,
            "results": self.test_results,
        }
        report_file = os.path.join(os.path.dirname(__file__), "test_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Test report saved to: {report_file}")


def main():
    """Main entry point."""
    tester = CertifiedMathTest()
    success = tester.run_tests()
    raise ZeroSimAbort(0 if success else 1)


if __name__ == "__main__":
    main()
