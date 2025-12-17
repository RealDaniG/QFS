"""
Test suite for HumorSignalAddon
"""
import unittest
import pytest
from .humor import HumorSignalAddon

class TestHumorSignalAddon(unittest.TestCase):
    """Test cases for HumorSignalAddon"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.addon = HumorSignalAddon()

    def test_initialization(self):
        """Test that the addon initializes correctly."""
        self.assertEqual(self.addon.addon_id, 'humor_signal_addon')

    def test_evaluate_deterministic(self):
        """Test that evaluations are deterministic."""
        content = "Why don't scientists trust atoms? Because they make up everything!"
        context = {'views': 100, 'laughs': 50, 'saves': 20, 'replays': 30, 'author_reputation': 0.8}
        result1 = self.addon.evaluate(content, context)
        result2 = self.addon.evaluate(content, context)
        self.assertEqual(result1.score, result2.score)
        self.assertEqual(result1.confidence, result2.confidence)
        self.assertEqual(result1.result_hash, result2.result_hash)
        self.assertEqual(result1.metadata, result2.metadata)

    def test_dimensions_structure(self):
        """Test that the result contains the correct dimension structure."""
        content = 'This is a test post with some humor content.'
        context = {'views': 50, 'laughs': 10, 'saves': 5, 'replays': 15, 'author_reputation': 0.6}
        result = self.addon.evaluate(content, context)
        self.assertIn('signal', result.metadata)
        self.assertIn('version', result.metadata)
        self.assertIn('dimensions', result.metadata)
        self.assertIn('ledger_context', result.metadata)
        self.assertEqual(result.metadata['signal'], 'comedic_value')
        self.assertEqual(result.metadata['version'], 'v1')
        dimensions = result.metadata['dimensions']
        self.assertIsInstance(dimensions, dict)
        self.assertEqual(len(dimensions), 7)
        expected_dimensions = ['chronos', 'lexicon', 'surreal', 'empathy', 'critique', 'slapstick', 'meta']
        for dim in expected_dimensions:
            self.assertIn(dim, dimensions)
            self.assertIsInstance(dimensions[dim], float)
            self.assertGreaterEqual(dimensions[dim], 0.0)
            self.assertLessEqual(dimensions[dim], 1.0)

    def test_ledger_context(self):
        """Test that ledger context is preserved."""
        content = 'Funny content here!'
        context = {'views': 123, 'laughs': 45, 'saves': 12, 'replays': 67, 'author_reputation': 0.75}
        result = self.addon.evaluate(content, context)
        ledger_context = result.metadata['ledger_context']
        self.assertEqual(ledger_context['views'], 123)
        self.assertEqual(ledger_context['laughs'], 45)
        self.assertEqual(ledger_context['saves'], 12)
        self.assertEqual(ledger_context['replays'], 67)
        self.assertEqual(ledger_context['author_reputation'], 0.75)

    def test_confidence_calculation(self):
        """Test confidence calculation with different engagement levels."""
        content = 'Test content'
        low_context = {'views': 10, 'laughs': 2, 'saves': 1, 'replays': 3, 'author_reputation': 0.5}
        high_context = {'views': 1000, 'laughs': 200, 'saves': 100, 'replays': 300, 'author_reputation': 0.9}
        low_result = self.addon.evaluate(content, low_context)
        high_result = self.addon.evaluate(content, high_context)
        self.assertGreater(high_result.confidence, low_result.confidence)
        self.assertGreaterEqual(low_result.confidence, 0.0)
        self.assertLessEqual(low_result.confidence, 1.0)
        self.assertGreaterEqual(high_result.confidence, 0.0)
        self.assertLessEqual(high_result.confidence, 1.0)

    def test_zero_engagement(self):
        """Test behavior with zero engagement metrics."""
        content = 'Test content'
        context = {'views': 0, 'laughs': 0, 'saves': 0, 'replays': 0, 'author_reputation': 0.5}
        result = self.addon.evaluate(content, context)
        self.assertIsInstance(result.score, float)
        self.assertIsInstance(result.confidence, float)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        dimensions = result.metadata['dimensions']
        for dim_value in dimensions.values():
            self.assertIsInstance(dim_value, float)
            self.assertGreaterEqual(dim_value, 0.0)
            self.assertLessEqual(dim_value, 1.0)
if __name__ == '__main__':
    unittest.main()