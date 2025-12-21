"""
Test suite for SignalAddon base class
"""
from fractions import Fraction
import unittest
from .base import SignalAddon, SignalResult

class TestSignalAddonBase(unittest.TestCase):
    """Test cases for SignalAddon base class"""

    def test_signal_result_creation(self):
        """Test that SignalResult is created correctly."""
        result = SignalResult(addon_id='test_addon', score=Fraction(17, 20), confidence=Fraction(23, 25), metadata={'test': 'data'}, content_hash='abc123', context_hash='def456', result_hash='')
        self.assertEqual(result.addon_id, 'test_addon')
        self.assertEqual(result.score, Fraction(17, 20))
        self.assertEqual(result.confidence, Fraction(23, 25))
        self.assertEqual(result.metadata, {'test': 'data'})
        self.assertEqual(result.content_hash, 'abc123')
        self.assertEqual(result.context_hash, 'def456')
        self.assertIsInstance(result.result_hash, str)
        self.assertNotEqual(result.result_hash, '')

    def test_signal_result_deterministic_hash(self):
        """Test that SignalResult generates deterministic hashes."""
        result1 = SignalResult(addon_id='test_addon', score=Fraction(17, 20), confidence=Fraction(23, 25), metadata={'test': 'data'}, content_hash='abc123', context_hash='def456', result_hash='')
        result2 = SignalResult(addon_id='test_addon', score=Fraction(17, 20), confidence=Fraction(23, 25), metadata={'test': 'data'}, content_hash='abc123', context_hash='def456', result_hash='')
        self.assertEqual(result1.result_hash, result2.result_hash)

    def test_signal_addon_abstract_methods(self):
        """Test that SignalAddon properly enforces abstract methods."""

        class IncompleteAddon(SignalAddon):
            pass
        addon = IncompleteAddon('test_addon')
        with self.assertRaises(NotImplementedError):
            addon.evaluate('test content', {'test': 'context'})

    def test_signal_addon_validation(self):
        """Test that SignalAddon validates inputs correctly."""

        class TestAddon(SignalAddon):

            def _evaluate_content(self, content: str, context: dict):
                return (Fraction(1, 2), Fraction(4, 5), {'test': 'data'})
        addon = TestAddon('test_addon')
        result = addon.evaluate('test content', {'test': 'context'})
        self.assertIsInstance(result, SignalResult)
        with self.assertRaises(ValueError):
            addon.evaluate(123, {'test': 'context'})
        with self.assertRaises(ValueError):
            addon.evaluate('test content', 'not a dict')
if __name__ == '__main__':
    unittest.main()