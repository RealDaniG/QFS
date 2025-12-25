"""
test_deterministic_components.py - Tests for Deterministic Components

Verifies that the new deterministic components work correctly and maintain Zero-Simulation compliance.
"""

from fractions import Fraction

import unittest
import sys
import os

# Add the v13 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v13"))


class TestQAmount(unittest.TestCase):
    """Test the QAmount economic quantity type."""

    def setUp(self):
        """Set up test fixtures."""
        from v13.libs.economics.QAmount import QAmount

        self.QAmount = QAmount

    def test_initialization(self):
        """Test QAmount initialization from various types."""
        # Test from int
        q1 = self.QAmount(10)
        self.assertIsInstance(q1, self.QAmount)

        # Test from string
        q2 = self.QAmount("10.5")
        self.assertIsInstance(q2, self.QAmount)

        # Test from float
        q3 = self.QAmount(Fraction(21, 2))
        self.assertIsInstance(q3, self.QAmount)

        # Test copy constructor
        q4 = self.QAmount(q1)
        self.assertIsInstance(q4, self.QAmount)
        self.assertEqual(q1, q4)

    def test_arithmetic_operations(self):
        """Test arithmetic operations."""
        q1 = self.QAmount(10)
        q2 = self.QAmount(5)

        # Test addition
        q3 = q1 + q2
        self.assertEqual(str(q3), "15.000000000000000000")

        # Test subtraction
        q4 = q1 - q2
        self.assertEqual(str(q4), "5.000000000000000000")

        # Test multiplication
        q5 = q1 * q2
        self.assertEqual(str(q5), "50.000000000000000000")

        # Test division
        q6 = q1 / q2
        self.assertEqual(str(q6), "2.000000000000000000")

    def test_comparison_operations(self):
        """Test comparison operations."""
        q1 = self.QAmount(10)
        q2 = self.QAmount(5)
        q3 = self.QAmount(10)

        # Test equality
        self.assertEqual(q1, q3)
        self.assertNotEqual(q1, q2)

        # Test ordering
        self.assertTrue(q1 > q2)
        self.assertTrue(q2 < q1)
        self.assertTrue(q1 >= q3)
        self.assertTrue(q2 <= q1)

    def test_serialization(self):
        """Test serialization to/from canonical JSON."""
        original = self.QAmount("123.456")

        # Test serialization
        json_str = original.to_canonical_json()
        self.assertIsInstance(json_str, str)
        self.assertIn(".", json_str)

        # Test deserialization
        restored = self.QAmount.from_canonical_json(json_str)
        self.assertEqual(original, restored)


class TestDeterministicTime(unittest.TestCase):
    """Test deterministic time functions."""

    def setUp(self):
        """Set up test fixtures."""
        from v13.libs.deterministic.time import (
            det_time_now,
            det_perf_counter,
            det_time_isoformat,
        )

        self.det_time_now = det_time_now
        self.det_perf_counter = det_perf_counter
        self.det_time_isoformat = det_time_isoformat

    def test_det_time_now(self):
        """Test deterministic time function."""
        t1 = self.det_time_now()
        t2 = self.det_time_now()

        # Should return the same value each time
        self.assertEqual(t1, t2)
        self.assertIsInstance(t1, int)

    def test_det_perf_counter(self):
        """Test deterministic performance counter."""
        c1 = self.det_perf_counter()
        c2 = self.det_perf_counter()

        # Should return the same value each time
        self.assertEqual(c1, c2)
        self.assertIsInstance(c1, float)

    def test_det_time_isoformat(self):
        """Test deterministic ISO format time."""
        iso1 = self.det_time_isoformat()
        iso2 = self.det_time_isoformat()

        # Should return the same value each time
        self.assertEqual(iso1, iso2)
        self.assertIsInstance(iso1, str)
        self.assertIn("T", iso1)
        self.assertIn(":", iso1)


class TestDeterministicRandom(unittest.TestCase):
    """Test deterministic random functions."""

    def setUp(self):
        """Set up test fixtures."""
        from v13.libs.deterministic.random import (
            det_random,
            det_randint,
            det_choice,
            det_seed,
        )

        self.det_random = det_random
        self.det_randint = det_randint
        self.det_choice = det_choice
        self.det_seed = det_seed

    def test_det_random(self):
        """Test deterministic random function."""
        # Reset seed for reproducible results
        self.det_seed(12345)

        r1 = self.det_random()
        r2 = self.det_random()

        # Should return deterministic values
        self.assertIsInstance(r1, float)
        self.assertIsInstance(r2, float)
        self.assertGreaterEqual(r1, 0)
        self.assertLess(r1, 1)

        # Reset seed again to get the same sequence
        self.det_seed(12345)
        r3 = self.det_random()
        r4 = self.det_random()

        self.assertEqual(r1, r3)
        self.assertEqual(r2, r4)

    def test_det_randint(self):
        """Test deterministic randint function."""
        # Reset seed for reproducible results
        self.det_seed(54321)

        i1 = self.det_randint(1, 10)
        i2 = self.det_randint(1, 10)

        # Should return deterministic values in range
        self.assertIsInstance(i1, int)
        self.assertIsInstance(i2, int)
        self.assertGreaterEqual(i1, 1)
        self.assertLessEqual(i1, 10)
        self.assertGreaterEqual(i2, 1)
        self.assertLessEqual(i2, 10)

    def test_det_choice(self):
        """Test deterministic choice function."""
        # Reset seed for reproducible results
        self.det_seed(98765)

        seq = [1, 2, 3, 4, 5]
        c1 = self.det_choice(seq)
        c2 = self.det_choice(seq)

        # Should return deterministic values from sequence
        self.assertIn(c1, seq)
        self.assertIn(c2, seq)


class TestFatalErrors(unittest.TestCase):
    """Test fatal error hierarchy."""

    def setUp(self):
        """Set up test fixtures."""
        from v13.libs.fatal_errors import (
            ZeroSimAbort,
            EconomicInvariantBreach,
            GovernanceGuardFailure,
        )

        self.ZeroSimAbort = ZeroSimAbort
        self.EconomicInvariantBreach = EconomicInvariantBreach
        self.GovernanceGuardFailure = GovernanceGuardFailure

    def test_zero_sim_abort(self):
        """Test ZeroSimAbort exception."""
        exc = self.ZeroSimAbort("Test message", 42)
        self.assertIsInstance(exc, Exception)
        self.assertEqual(exc.exit_code, 42)
        self.assertIn("Test message", str(exc))
        self.assertIn("exit code: 42", str(exc))

    def test_economic_invariant_breach(self):
        """Test EconomicInvariantBreach exception."""
        exc = self.EconomicInvariantBreach("supply_limit", "Exceeded maximum supply")
        self.assertIsInstance(exc, self.ZeroSimAbort)
        self.assertEqual(exc.exit_code, 10)
        self.assertIn("supply_limit", str(exc))
        self.assertIn("Exceeded maximum supply", str(exc))

    def test_governance_guard_failure(self):
        """Test GovernanceGuardFailure exception."""
        exc = self.GovernanceGuardFailure("proposal_quorum", "Insufficient votes")
        self.assertIsInstance(exc, self.ZeroSimAbort)
        self.assertEqual(exc.exit_code, 20)
        self.assertIn("proposal_quorum", str(exc))
        self.assertIn("Insufficient votes", str(exc))


class TestAtlasAdapters(unittest.TestCase):
    """Test ATLAS-facing adapters."""

    def setUp(self):
        """Set up test fixtures."""
        from v13.libs.economics.QAmount import QAmount
        from v13.atlas.src.numeric import AtlasNumeric
        from v13.atlas.src.time import AtlasTime

        self.QAmount = QAmount
        self.AtlasNumeric = AtlasNumeric
        self.AtlasTime = AtlasTime

    def test_atlas_numeric(self):
        """Test ATLAS numeric adapter."""
        # Test conversion
        amount = self.AtlasNumeric.to_atlas_amount(100)
        self.assertIsInstance(amount, self.QAmount)

        # Test serialization
        json_str = self.AtlasNumeric.serialize_amount(amount)
        self.assertIsInstance(json_str, str)
        self.assertIn(".", json_str)

        # Test deserialization
        restored = self.AtlasNumeric.deserialize_amount(json_str)
        self.assertEqual(amount, restored)

    def test_atlas_time(self):
        """Test ATLAS time adapter."""
        # Test timestamp
        ts = self.AtlasTime.current_timestamp()
        self.assertIsInstance(ts, int)

        # Test ISO format
        iso = self.AtlasTime.iso_format_timestamp()
        self.assertIsInstance(iso, str)
        self.assertIn("T", iso)

        # Test serialization
        serialized = self.AtlasTime.serialize_timestamp(ts)
        self.assertEqual(serialized, str(ts))


if __name__ == "__main__":
    unittest.main()
