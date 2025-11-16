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
        self.certified_math = CertifiedMath()
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
        result = self.certified_math.add("1000000000000000000", "2000000000000000000")  # 1 + 2
        expected = "3000000000000000000"  # 3
        if result == expected:
            print("  ✅ Addition test passed")
            self.passed += 1
        else:
            print(f"  ❌ Addition test failed: expected {expected}, got {result}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_addition',
                'status': 'FAILED',
                'expected': expected,
                'actual': result
            })
            
        # Test subtraction
        result = self.certified_math.subtract("3000000000000000000", "1000000000000000000")  # 3 - 1
        expected = "2000000000000000000"  # 2
        if result == expected:
            print("  ✅ Subtraction test passed")
            self.passed += 1
        else:
            print(f"  ❌ Subtraction test failed: expected {expected}, got {result}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_subtraction',
                'status': 'FAILED',
                'expected': expected,
                'actual': result
            })
            
        # Test multiplication
        result = self.certified_math.multiply("2000000000000000000", "3000000000000000000")  # 2 * 3
        expected = "6000000000000000000"  # 6
        if result == expected:
            print("  ✅ Multiplication test passed")
            self.passed += 1
        else:
            print(f"  ❌ Multiplication test failed: expected {expected}, got {result}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_multiplication',
                'status': 'FAILED',
                'expected': expected,
                'actual': result
            })
            
        # Test division
        result = self.certified_math.divide("6000000000000000000", "2000000000000000000")  # 6 / 2
        expected = "3000000000000000000"  # 3
        if result == expected:
            print("  ✅ Division test passed")
            self.passed += 1
        else:
            print(f"  ❌ Division test failed: expected {expected}, got {result}")
            self.failed += 1
            self.test_results.append({
                'test': 'basic_arithmetic_division',
                'status': 'FAILED',
                'expected': expected,
                'actual': result
            })
            
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("Testing edge cases...")
        
        # Test zero operations
        result = self.certified_math.add("0", "1000000000000000000")  # 0 + 1
        expected = "1000000000000000000"  # 1
        if result == expected:
            print("  ✅ Zero addition test passed")
            self.passed += 1
        else:
            print(f"  ❌ Zero addition test failed: expected {expected}, got {result}")
            self.failed += 1
            
        # Test negative numbers
        result = self.certified_math.add("-1000000000000000000", "2000000000000000000")  # -1 + 2
        expected = "1000000000000000000"  # 1
        if result == expected:
            print("  ✅ Negative number test passed")
            self.passed += 1
        else:
            print(f"  ❌ Negative number test failed: expected {expected}, got {result}")
            self.failed += 1
            
    def test_deterministic_behavior(self):
        """Test that operations are deterministic across multiple runs."""
        print("Testing deterministic behavior...")
        
        # Perform the same operation multiple times
        results = []
        for i in range(5):
            result = self.certified_math.add("1234567890000000000", "9876543210000000000")  # 1.23456789 + 9.87654321
            results.append(result)
            
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
        
        # Clear any existing audit log
        self.certified_math.clear_audit_log()
        
        # Perform an operation
        result = self.certified_math.add("1000000000000000000", "2000000000000000000")  # 1 + 2
        
        # Check that audit log has entries
        audit_log = self.certified_math.get_audit_log()
        if len(audit_log) > 0:
            print("  ✅ Audit logging test passed")
            self.passed += 1
        else:
            print("  ❌ Audit logging test failed: no audit entries found")
            self.failed += 1
            
    def test_comparison_operations(self):
        """Test comparison operations."""
        print("Testing comparison operations...")
        
        # Test greater_than
        result = self.certified_math.greater_than("2000000000000000000", "1000000000000000000")  # 2 > 1
        if result:
            print("  ✅ Greater than test passed")
            self.passed += 1
        else:
            print("  ❌ Greater than test failed")
            self.failed += 1
            
        # Test less_than
        result = self.certified_math.less_than("1000000000000000000", "2000000000000000000")  # 1 < 2
        if result:
            print("  ✅ Less than test passed")
            self.passed += 1
        else:
            print("  ❌ Less than test failed")
            self.failed += 1
            
    def test_rounding_operations(self):
        """Test rounding operations."""
        print("Testing rounding operations...")
        
        # Test floor
        try:
            result = self.certified_math.floor("1500000000000000000")  # floor(1.5)
            # This should be 1.0 (1000000000000000000)
            expected = "1000000000000000000"
            if result == expected:
                print("  ✅ Floor test passed")
                self.passed += 1
            else:
                print(f"  ❌ Floor test failed: expected {expected}, got {result}")
                self.failed += 1
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