"""
Zero-Simulation Compliance Test for HumorSignalAddon
"""

import unittest
import pytest
from .humor import HumorSignalAddon


class TestHumorSignalAddonZeroSimCompliance(unittest.TestCase):
    """Test cases for HumorSignalAddon Zero-Simulation compliance"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.addon = HumorSignalAddon()
    
    def test_no_composite_score_calculation(self):
        """Test that no composite score is calculated internally."""
        content = "Why don't scientists trust atoms? Because they make up everything!"
        context = {
            "views": 100,
            "laughs": 50,
            "saves": 20,
            "replays": 30,
            "author_reputation": 0.8
        }
        
        result = self.addon.evaluate(content, context)
        
        # The addon should return a dummy score of 0.0
        # Actual aggregation happens in PolicyRegistry/TreasuryEngine
        self.assertEqual(result.score, 0.0)
    
    def test_deterministic_behavior(self):
        """Test that evaluations are fully deterministic."""
        content = "Why don't scientists trust atoms? Because they make up everything!"
        context = {
            "views": 100,
            "laughs": 50,
            "saves": 20,
            "replays": 30,
            "author_reputation": 0.8
        }
        
        result1 = self.addon.evaluate(content, context)
        result2 = self.addon.evaluate(content, context)
        
        # Results should be identical
        self.assertEqual(result1.score, result2.score)
        self.assertEqual(result1.confidence, result2.confidence)
        self.assertEqual(result1.result_hash, result2.result_hash)
        self.assertEqual(result1.metadata, result2.metadata)
        
        # Check that dimensions are also identical
        self.assertEqual(
            result1.metadata["dimensions"], 
            result2.metadata["dimensions"]
        )
    
    def test_pure_vector_signal_provider(self):
        """Test that the addon is a pure vector signal provider."""
        content = "This is a test post with some humor content."
        context = {
            "views": 50,
            "laughs": 10,
            "saves": 5,
            "replays": 15,
            "author_reputation": 0.6
        }
        
        result = self.addon.evaluate(content, context)
        
        # Check that we have the expected structure
        self.assertIn("signal", result.metadata)
        self.assertIn("version", result.metadata)
        self.assertIn("dimensions", result.metadata)
        self.assertIn("ledger_context", result.metadata)
        
        # Check signal metadata
        self.assertEqual(result.metadata["signal"], "comedic_value")
        self.assertEqual(result.metadata["version"], "v1")
        
        # Check dimensions
        dimensions = result.metadata["dimensions"]
        self.assertIsInstance(dimensions, dict)
        self.assertEqual(len(dimensions), 7)
        
        # Check all 7 dimensions are present
        expected_dimensions = ["chronos", "lexicon", "surreal", "empathy", "critique", "slapstick", "meta"]
        for dim in expected_dimensions:
            self.assertIn(dim, dimensions)
            self.assertIsInstance(dimensions[dim], float)
            self.assertGreaterEqual(dimensions[dim], 0.0)
            self.assertLessEqual(dimensions[dim], 1.0)
    
    def test_ledger_derived_metrics_only(self):
        """Test that only ledger-derived metrics are used."""
        content = "Funny content here!"
        context = {
            "views": 123,
            "laughs": 45,
            "saves": 12,
            "replays": 67,
            "author_reputation": 0.75
        }
        
        result = self.addon.evaluate(content, context)
        
        # Verify that no wall-clock or timestamp usage exists
        # This is verified by the deterministic nature of the tests
        # and by ensuring no time-based operations in the implementation
        
        # Check that ledger context is preserved
        ledger_context = result.metadata["ledger_context"]
        self.assertEqual(ledger_context["views"], 123)
        self.assertEqual(ledger_context["laughs"], 45)
        self.assertEqual(ledger_context["saves"], 12)
        self.assertEqual(ledger_context["replays"], 67)
        self.assertEqual(ledger_context["author_reputation"], 0.75)
    
    def test_deterministic_text_processing(self):
        """Test that text processing is deterministic."""
        content1 = "Test content with emojis 😀 and exclamation marks!!!"
        content2 = "Test content with emojis 😀 and exclamation marks!!!"
        
        context = {
            "views": 100,
            "laughs": 50,
            "saves": 25,
            "replays": 30,
            "author_reputation": 0.8
        }
        
        result1 = self.addon.evaluate(content1, context)
        result2 = self.addon.evaluate(content2, context)
        
        # Identical content should produce identical results
        self.assertEqual(result1.metadata["dimensions"], result2.metadata["dimensions"])
    
    def test_confidence_based_on_ledger_metrics(self):
        """Test that confidence is based purely on ledger-derived metrics."""
        content = "Test content"
        
        # Low engagement
        low_context = {
            "views": 10,
            "laughs": 2,
            "saves": 1,
            "replays": 3,
            "author_reputation": 0.5
        }
        
        # High engagement
        high_context = {
            "views": 1000,
            "laughs": 200,
            "saves": 100,
            "replays": 300,
            "author_reputation": 0.9
        }
        
        low_result = self.addon.evaluate(content, low_context)
        high_result = self.addon.evaluate(content, high_context)
        
        # Higher engagement should lead to higher confidence
        self.assertGreater(high_result.confidence, low_result.confidence)
        
        # Confidence should be in [0,1]
        self.assertGreaterEqual(low_result.confidence, 0.0)
        self.assertLessEqual(low_result.confidence, 1.0)
        self.assertGreaterEqual(high_result.confidence, 0.0)
        self.assertLessEqual(high_result.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()