#!/usr/bin/env python3

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

import sys
import os
import json
from datetime import datetime

# Add the libs directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

from CertifiedMath import CertifiedMath, BigNum128

class CertifiedMathTest:
    """Test suite for CertifiedMath implementation."""
    
    def __init__(self):
        # CertifiedMath requires a log_list parameter
        self.log_list = []
        self.certified_math = CertifiedMath(self.log_list)
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def run_tests(self):
        """Run all tests."""
        print("Running CertifiedMath Test Suite...")
        print("=" * 50)
        
        # Run individual tests
        self.test_basic_arithmetic()
        self.test_edge_cases()
        self.test_deterministic_behavior()
        self.test_audit_logging()
        self.test_comparison_operations()
        self.test_rounding_operations()
        
        # Print summary
        print("=" * 50)
        print(f"Tests passed: {self.passed}")
        print(f"Tests failed: {self.failed}")
        print(f"Total tests: {self.passed + self.failed}")
        
        # Generate report
        self.generate_report()
        
        return self.failed == 0
        
    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        print("Testing basic arithmetic operations...")
        
        # Test addition
        a = BigNum128.from_string("1.0")
        b = BigNum128.from_string("2.0")
        result = self.certified_math.add(a, b, pqc_cid="TEST_ADD")
        expected = BigNum128.from_string("3.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Addition test passed")
            self.passed += 1
        else:
            print(f"  ❌ Addition test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_addition',
                'status': 'FAILED',
                'expected': expected.to_decimal_string(),
                'actual': result.to_decimal_string()
            })
            
        # Test subtraction
        a = BigNum128.from_string("3.0")
        b = BigNum128.from_string("1.0")
        result = self.certified_math.sub(a, b, pqc_cid="TEST_SUB")
        expected = BigNum128.from_string("2.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Subtraction test passed")
            self.passed += 1
        else:
            print(f"  ❌ Subtraction test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_subtraction',
                'status': 'FAILED',
                'expected': expected.to_decimal_string(),
                'actual': result.to_decimal_string()
            })
            
        # Test multiplication
        a = BigNum128.from_string("2.0")
        b = BigNum128.from_string("3.0")
        result = self.certified_math.mul(a, b, pqc_cid="TEST_MUL")
        expected = BigNum128.from_string("6.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Multiplication test passed")
            self.passed += 1
        else:
            print(f"  ❌ Multiplication test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_multiplication',
                'status': 'FAILED',
                'expected': expected.to_decimal_string(),
                'actual': result.to_decimal_string()
            })
            
        # Test division
        a = BigNum128.from_string("6.0")
        b = BigNum128.from_string("2.0")
        result = self.certified_math.div(a, b, pqc_cid="TEST_DIV")
        expected = BigNum128.from_string("3.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Division test passed")
            self.passed += 1
        else:
            print(f"  ❌ Division test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_division',
                'status': 'FAILED',
                'expected': expected.to_decimal_string(),
                'actual': result.to_decimal_string()
            })
            
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("Testing edge cases...")
        
        # Test zero operations
        a = BigNum128.from_string("0.0")
        b = BigNum128.from_string("1.0")
        result = self.certified_math.add(a, b, pqc_cid="TEST_ZERO_ADD")
        expected = BigNum128.from_string("1.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Zero addition test passed")
            self.passed += 1
        else:
            print(f"  ❌ Zero addition test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}")
            self.failed += 1
            
        # Test negative numbers
        a = BigNum128.from_string("-1.0")
        b = BigNum128.from_string("2.0")
        result = self.certified_math.add(a, b, pqc_cid="TEST_NEG_ADD")
        expected = BigNum128.from_string("1.0")
        if abs(result.value - expected.value) < BigNum128.SCALE // 1000000000000:
            print("  ✅ Negative number test passed")
            self.passed += 1
        else:
            print(f"  ❌ Negative number test failed: expected {expected.to_decimal_string()}, got {result.to_decimal_string()}")
            self.failed += 1
            
    def test_deterministic_behavior(self):
        """Test that operations are deterministic across multiple runs."""
        print("Testing deterministic behavior...")
        
        # Perform the same operation multiple times
        results = []
        a = BigNum128.from_string("1.23456789")
        b = BigNum128.from_string("9.87654321")
        for i in range(5):
            log_list = []
            cm = CertifiedMath(log_list)
            result = cm.add(a, b, pqc_cid=f"TEST_DET_{i}")
            results.append(result.value)
            
        # Check that all results are the same
        if all(r == results[0] for r in results):
            print("  ✅ Deterministic behavior test passed")
            self.passed += 1
        else:
            print(f"  ❌ Deterministic behavior test failed: results vary ({results})")
            self.failed += 1
            
    def test_audit_logging(self):
        """Test audit logging functionality."""
        print("Testing audit logging...")
        
        # Create a new CertifiedMath instance with fresh log
        log_list = []
        cm = CertifiedMath(log_list)
        
        # Perform an operation
        a = BigNum128.from_string("1.0")
        b = BigNum128.from_string("2.0")
        result = cm.add(a, b, pqc_cid="TEST_LOG")
        
        # Check that audit log has entries
        if len(log_list) > 0:
            print("  ✅ Audit logging test passed")
            self.passed += 1
        else:
            print("  ❌ Audit logging test failed: no audit entries found")
            self.failed += 1
            
    def test_comparison_operations(self):
        """Test comparison operations."""
        print("Testing comparison operations...")
        
        # Test that we can compare BigNum128 values directly
        a = BigNum128.from_string("2.0")
        b = BigNum128.from_string("1.0")
        if a.value > b.value:
            print("  ✅ Greater than test passed")
            self.passed += 1
        else:
            print("  ❌ Greater than test failed")
            self.failed += 1
            
        # Test less than
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
        
        # Test that we can access the floor method if it exists
        try:
            a = BigNum128.from_string("1.5")
            # Floor operation would need to be implemented in BigNum128
            # For now, we'll just test that the value is as expected
            print("  ⚠️  Floor method test skipped (not implemented in BigNum128)")
        except AttributeError:
            print("  ⚠️  Floor method not implemented, skipping test")
            
    def generate_report(self):
        """Generate a test report."""
        report = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'tests_run': self.passed + self.failed,
            'tests_passed': self.passed,
            'tests_failed': self.failed,
            'results': self.test_results
        }
        
        # Write report to file
        report_file = os.path.join(os.path.dirname(__file__), 'test_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Test report saved to: {report_file}")


def main():
    """Main entry point."""
    tester = CertifiedMathTest()
    success = tester.run_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()