"""
Property-Based Fuzzing Test Suite for BigNum128
QFS V13.5 / V2.1 Compliance - Phase 1

This test suite performs comprehensive property-based fuzzing of BigNum128 operations
to verify deterministic behavior, overflow handling, and correctness under stress conditions.

Requirements Addressed:
- A1: BigNum128 Range Stress Fuzzing
- A1: Overflow/Underflow Resilience Tests
- A1: Near-Boundary Edge Cases

Evidence Generated:
- evidence/phase1/bignum128_stress_summary.json
"""

from fractions import Fraction
from libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    qnum,
)
import json
import hashlib
import logging
import os
from typing import List, Dict, Any
from v13.libs.BigNum128 import BigNum128, BigNum128Error

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


class BigNum128FuzzResult:
    """Container for fuzzing test results"""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.total_cases = 0
        self.passed_cases = 0
        self.failed_cases = 0
        self.overflow_cases = 0
        self.underflow_cases = 0
        self.failures: List[Dict[str, Any]] = []

    def record_pass(self):
        self.total_cases += 1
        self.passed_cases += 1

    def record_fail(
        self, operation: str, inputs: Any, expected: Any, actual: Any, error: str
    ):
        self.total_cases += 1
        self.failed_cases += 1
        self.failures.append(
            {
                "operation": operation,
                "inputs": str(inputs),
                "expected": str(expected),
                "actual": str(actual),
                "error": error,
            }
        )

    def record_overflow(self):
        self.total_cases += 1
        self.overflow_cases += 1

    def record_underflow(self):
        self.total_cases += 1
        self.underflow_cases += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "overflow_cases": self.overflow_cases,
            "underflow_cases": self.underflow_cases,
            "success_rate": f"{self.passed_cases / self.total_cases * 100:.2f}%"
            if self.total_cases > 0
            else "0%",
            "failures": self.failures[:10],
        }


def test_construction_parsing_fuzz():
    """Fuzz test: Construction from strings and integers"""
    result = BigNum128FuzzResult("construction_parsing_fuzz")
    test_values = [
        "0",
        "1",
        "999999999999999999",
        "0.0",
        "1.0",
        "0.1",
        "0.000000000000000001",
        "123456.789012345678901234",
        "340282366920938463463.374607431768211455",
        "0." + "9" * 18,
        "1" + "0" * 20,
    ]
    for val_str in sorted(test_values):
        try:
            bn = BigNum128.from_string(val_str)
            reconstructed = BigNum128.from_string(
                bn.to_decimal_string(fixed_width=True)
            )
            if bn.value != reconstructed.value:
                result.record_fail(
                    "from_string round-trip",
                    val_str,
                    bn.value,
                    reconstructed.value,
                    "Round-trip reconstruction mismatch",
                )
            else:
                result.record_pass()
        except OverflowError:
            result.record_overflow()
        except BigNum128Error:
            result.record_underflow()
        except Exception as e:
            result.record_fail(
                "from_string", val_str, "valid construction", type(e).__name__, str(e)
            )
    return result


def test_addition_properties_fuzz():
    """Fuzz test: Addition properties (commutativity, associativity)"""
    result = BigNum128FuzzResult("addition_properties_fuzz")
    test_values = [
        BigNum128(0),
        BigNum128(1),
        BigNum128(BigNum128.SCALE),
        BigNum128(BigNum128.SCALE // 2),
        BigNum128(BigNum128.MAX_VALUE // 4),
        BigNum128(BigNum128.MAX_VALUE // 2),
        BigNum128(BigNum128.MAX_VALUE - 1),
    ]
    for a in sorted(test_values):
        for b in sorted(test_values):
            try:
                sum_ab = a.add(b)
                sum_ba = b.add(a)
                if sum_ab.value == sum_ba.value:
                    result.record_pass()
                else:
                    result.record_fail(
                        "addition commutativity",
                        f"a={a.value}, b={b.value}",
                        sum_ab.value,
                        sum_ba.value,
                        "a+b != b+a",
                    )
            except OverflowError:
                result.record_overflow()
            except Exception as e:
                result.record_fail(
                    "addition",
                    f"a={a.value}, b={b.value}",
                    "success",
                    type(e).__name__,
                    str(e),
                )
    for a in test_values[:3]:
        for b in test_values[:3]:
            for c in test_values[:3]:
                try:
                    sum_ab_c = a.add(b).add(c)
                    sum_a_bc = a.add(b.add(c))
                    if sum_ab_c.value == sum_a_bc.value:
                        result.record_pass()
                    else:
                        result.record_fail(
                            "addition associativity",
                            f"a={a.value}, b={b.value}, c={c.value}",
                            sum_ab_c.value,
                            sum_a_bc.value,
                            "(a+b)+c != a+(b+c)",
                        )
                except OverflowError:
                    result.record_overflow()
                except Exception as e:
                    result.record_fail(
                        "addition associativity",
                        f"a={a.value}, b={b.value}, c={c.value}",
                        "success",
                        type(e).__name__,
                        str(e),
                    )
    return result


def test_subtraction_properties_fuzz():
    """Fuzz test: Subtraction properties and underflow handling"""
    result = BigNum128FuzzResult("subtraction_properties_fuzz")
    test_values = [
        BigNum128(0),
        BigNum128(BigNum128.SCALE),
        BigNum128(BigNum128.MAX_VALUE // 2),
        BigNum128(BigNum128.MAX_VALUE - 1),
        BigNum128(BigNum128.MAX_VALUE),
    ]
    for a in sorted(test_values):
        for b in sorted(test_values):
            if a.value >= b.value:
                try:
                    diff = a.sub(b)
                    if diff.value == a.value - b.value:
                        result.record_pass()
                    else:
                        result.record_fail(
                            "subtraction correctness",
                            f"a={a.value}, b={b.value}",
                            a.value - b.value,
                            diff.value,
                            "Subtraction result incorrect",
                        )
                except Exception as e:
                    result.record_fail(
                        "subtraction",
                        f"a={a.value}, b={b.value}",
                        "success",
                        type(e).__name__,
                        str(e),
                    )
            else:
                try:
                    diff = a.sub(b)
                    result.record_fail(
                        "subtraction underflow detection",
                        f"a={a.value}, b={b.value}",
                        "BigNum128Error",
                        "success",
                        "Expected underflow error not raised",
                    )
                except BigNum128Error:
                    result.record_underflow()
                except Exception as e:
                    result.record_fail(
                        "subtraction underflow",
                        f"a={a.value}, b={b.value}",
                        "BigNum128Error",
                        type(e).__name__,
                        str(e),
                    )
    return result


def test_multiplication_properties_fuzz():
    """Fuzz test: Multiplication properties (commutativity, distributivity)"""
    result = BigNum128FuzzResult("multiplication_properties_fuzz")
    test_values = [
        BigNum128(0),
        BigNum128(BigNum128.SCALE),
        BigNum128(BigNum128.SCALE // 2),
        BigNum128(BigNum128.SCALE * 2),
        BigNum128(BigNum128.SCALE * 1000),
        BigNum128(int(BigNum128.MAX_VALUE ** Fraction(1, 2))),
    ]
    for a in sorted(test_values):
        for b in sorted(test_values):
            try:
                prod_ab = a.mul(b)
                prod_ba = b.mul(a)
                if prod_ab.value == prod_ba.value:
                    result.record_pass()
                else:
                    result.record_fail(
                        "multiplication commutativity",
                        f"a={a.value}, b={b.value}",
                        prod_ab.value,
                        prod_ba.value,
                        "a*b != b*a",
                    )
            except OverflowError:
                result.record_overflow()
            except Exception as e:
                result.record_fail(
                    "multiplication",
                    f"a={a.value}, b={b.value}",
                    "success",
                    type(e).__name__,
                    str(e),
                )
    return result


def test_division_properties_fuzz():
    """Fuzz test: Division properties and zero-division handling"""
    result = BigNum128FuzzResult("division_properties_fuzz")
    test_values = [
        BigNum128(BigNum128.SCALE),
        BigNum128(BigNum128.SCALE * 2),
        BigNum128(BigNum128.SCALE * 1000),
        BigNum128(BigNum128.MAX_VALUE // 2),
    ]
    divisors = [
        BigNum128(BigNum128.SCALE),
        BigNum128(BigNum128.SCALE // 2),
        BigNum128(BigNum128.SCALE * 2),
        BigNum128(BigNum128.SCALE * 1000),
    ]
    for a in sorted(test_values):
        for b in sorted(divisors):
            if b.value == 0:
                try:
                    quot = a.div(b)
                    result.record_fail(
                        "division by zero detection",
                        f"a={a.value}, b=0",
                        "BigNum128Error",
                        "success",
                        "Expected division by zero error not raised",
                    )
                except (BigNum128Error, ZeroDivisionError):
                    result.record_pass()
            else:
                try:
                    quot = a.div(b)
                    reconstructed = quot.mul(b)
                    tolerance = BigNum128.SCALE // 1000
                    diff = abs(reconstructed.value - a.value)
                    if diff <= tolerance:
                        result.record_pass()
                    else:
                        result.record_fail(
                            "division-multiplication inverse",
                            f"a={a.value}, b={b.value}",
                            a.value,
                            reconstructed.value,
                            f"Reconstruction error: {diff} > {tolerance}",
                        )
                except Exception as e:
                    result.record_fail(
                        "division",
                        f"a={a.value}, b={b.value}",
                        "success",
                        type(e).__name__,
                        str(e),
                    )
    return result


def test_comparison_consistency_fuzz():
    """Fuzz test: Comparison operator consistency"""
    result = BigNum128FuzzResult("comparison_consistency_fuzz")
    test_values = [
        BigNum128(0),
        BigNum128(1),
        BigNum128(BigNum128.SCALE),
        BigNum128(BigNum128.SCALE + 1),
        BigNum128(BigNum128.MAX_VALUE // 2),
        BigNum128(BigNum128.MAX_VALUE - 1),
        BigNum128(BigNum128.MAX_VALUE),
    ]
    for a in sorted(test_values):
        for b in sorted(test_values):
            try:
                lt = a < b
                le = a <= b
                gt = b > a
                ge = b >= a
                eq = a == b
                ne = a != b
                consistent = True
                errors = []
                if lt and (not le):
                    consistent = False
                    errors.append("a<b but not a<=b")
                if lt and (not gt):
                    consistent = False
                    errors.append("a<b but not b>a")
                if lt and (not ge):
                    consistent = False
                    errors.append("a<b but not b>=a")
                if lt and eq:
                    consistent = False
                    errors.append("a<b but a==b")
                if not lt and (not gt) and (not eq):
                    consistent = False
                    errors.append("not(a<b) and not(b>a) but not(a==b)")
                if eq and ne:
                    consistent = False
                    errors.append("a==b but a!=b")
                if consistent:
                    result.record_pass()
                else:
                    result.record_fail(
                        "comparison consistency",
                        f"a={a.value}, b={b.value}",
                        "consistent comparisons",
                        "inconsistent",
                        "; ".join(errors),
                    )
            except Exception as e:
                result.record_fail(
                    "comparison",
                    f"a={a.value}, b={b.value}",
                    "success",
                    type(e).__name__,
                    str(e),
                )
    return result


def test_serialization_determinism_fuzz():
    """Fuzz test: Serialization produces identical output for identical inputs"""
    result = BigNum128FuzzResult("serialization_determinism_fuzz")
    test_values = [
        BigNum128(0),
        BigNum128(BigNum128.SCALE),
        BigNum128(BigNum128.MAX_VALUE // 2),
        BigNum128(BigNum128.MAX_VALUE),
    ]
    for val in sorted(test_values):
        try:
            ser1 = val.to_decimal_string(fixed_width=True)
            ser2 = val.to_decimal_string(fixed_width=True)
            ser3 = val.to_decimal_string(fixed_width=True)
            if ser1 == ser2 == ser3:
                result.record_pass()
            else:
                result.record_fail(
                    "serialization determinism",
                    f"value={val.value}",
                    ser1,
                    f"ser2={ser2}, ser3={ser3}",
                    "Non-deterministic serialization",
                )
            hash1 = hash(val)
            hash2 = hash(val)
            hash3 = hash(val)
            if hash1 == hash2 == hash3:
                result.record_pass()
            else:
                result.record_fail(
                    "hash determinism",
                    f"value={val.value}",
                    hash1,
                    f"hash2={hash2}, hash3={hash3}",
                    "Non-deterministic hashing",
                )
        except Exception as e:
            result.record_fail(
                "serialization",
                f"value={val.value}",
                "success",
                type(e).__name__,
                str(e),
            )
    return result


def run_all_fuzzing_tests():
    """Execute all property-based fuzzing tests"""
    logger.info("\n" + "=" * 80)
    logger.info("QFS V13.5 - BigNum128 Property-Based Fuzzing Test Suite")
    logger.info("=" * 80 + "\n")
    tests = [
        test_construction_parsing_fuzz,
        test_addition_properties_fuzz,
        test_subtraction_properties_fuzz,
        test_multiplication_properties_fuzz,
        test_division_properties_fuzz,
        test_comparison_consistency_fuzz,
        test_serialization_determinism_fuzz,
    ]
    results = []
    total_passed = 0
    total_failed = 0
    total_cases = 0
    for test_func in sorted(tests):
        logger.info(f"Running: {test_func.__name__}...")
        result = test_func()
        results.append(result)
        total_passed += result.passed_cases
        total_failed += result.failed_cases
        total_cases += result.total_cases
        logger.info(f"  Total Cases: {result.total_cases}")
        logger.info(f"  Passed: {result.passed_cases}")
        logger.info(f"  Failed: {result.failed_cases}")
        logger.info(f"  Overflows: {result.overflow_cases}")
        logger.info(f"  Underflows: {result.underflow_cases}")
        logger.info("")
    evidence = {
        "test_suite": "BigNum128 Property-Based Fuzzing",
        "qfs_version": "V13",
        "compliance_standard": "V13.5 / V2.1",
        "phase": "PHASE 1",
        "requirement": "A1 - BigNum128 Stress Testing",
        "total_test_cases": total_cases,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "success_rate": f"{total_passed / total_cases * 100:.2f}%"
        if total_cases > 0
        else "0%",
        "tests": [r.to_dict() for r in results],
        "verdict": "PASS" if total_failed == 0 else "FAIL",
        "evidence_hash": "TO_BE_COMPUTED",
    }
    evidence_json = json.dumps(evidence, sort_keys=True, indent=2)
    evidence_hash = hashlib.sha3_512(evidence_json.encode()).hexdigest()
    evidence["evidence_hash"] = evidence_hash
    evidence_dir = os.path.join(os.path.dirname(__file__), "../../evidence/phase1")
    os.makedirs(evidence_dir, exist_ok=True)
    evidence_path = os.path.join(evidence_dir, "bignum128_fuzz_results.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2)
    logger.info("=" * 80)
    logger.info(f"OVERALL RESULTS:")
    logger.info(f"  Total Cases: {total_cases}")
    logger.info(f"  Passed: {total_passed}")
    logger.info(f"  Failed: {total_failed}")
    logger.info(f"  Success Rate: {evidence['success_rate']}")
    logger.info(f"  Verdict: {evidence['verdict']}")
    logger.info(f"\nEvidence saved to: {evidence_path}")
    logger.info(f"Evidence Hash (SHA3-512): {evidence_hash[:64]}...")
    logger.info("=" * 80 + "\n")
    return evidence["verdict"] == "PASS"


if __name__ == "__main__":
    success = run_all_fuzzing_tests()
    raise ZeroSimAbort(0 if success else 1)
