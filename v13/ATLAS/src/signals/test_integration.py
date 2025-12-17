"""
Integration test for SignalAddon and HumorSignalAddon
"""
import unittest
from .base import SignalAddon, SignalResult
from .humor import HumorSignalAddon

class TestSignalAddonIntegration(unittest.TestCase):
    """Integration tests for SignalAddon and HumorSignalAddon"""

    def test_humor_addon_integration(self):
        """Test that HumorSignalAddon integrates correctly with SignalAddon base."""
        addon = HumorSignalAddon()
        content = "Why don't scientists trust atoms? Because they make up everything! 😂"
        context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        result = addon.evaluate(content, context)
        self.assertIsInstance(result, SignalResult)
        self.assertEqual(result.addon_id, 'humor_signal_addon')
        self.assertIsInstance(result.score, float)
        self.assertIsInstance(result.confidence, float)
        self.assertIsInstance(result.metadata, dict)
        self.assertIsInstance(result.content_hash, str)
        self.assertIsInstance(result.context_hash, str)
        self.assertIsInstance(result.result_hash, str)
        metadata = result.metadata
        self.assertIn('signal', metadata)
        self.assertIn('version', metadata)
        self.assertIn('dimensions', metadata)
        self.assertIn('ledger_context', metadata)
        self.assertEqual(metadata['signal'], 'comedic_value')
        self.assertEqual(metadata['version'], 'v1')
        dimensions = metadata['dimensions']
        self.assertIsInstance(dimensions, dict)
        self.assertEqual(len(dimensions), 7)
        expected_dimensions = ['chronos', 'lexicon', 'surreal', 'empathy', 'critique', 'slapstick', 'meta']
        for dim in expected_dimensions:
            self.assertIn(dim, dimensions)
            self.assertIsInstance(dimensions[dim], float)
            self.assertGreaterEqual(dimensions[dim], 0.0)
            self.assertLessEqual(dimensions[dim], 1.0)
        ledger_context = metadata['ledger_context']
        self.assertEqual(ledger_context['views'], 1000)
        self.assertEqual(ledger_context['laughs'], 800)
        self.assertEqual(ledger_context['saves'], 200)
        self.assertEqual(ledger_context['replays'], 150)
        self.assertEqual(ledger_context['author_reputation'], 0.9)
        result2 = addon.evaluate(content, context)
        self.assertEqual(result.result_hash, result2.result_hash)
        self.assertEqual(result.metadata, result2.metadata)

    def test_empty_context_handling(self):
        """Test that the addon handles empty or minimal context gracefully."""
        addon = HumorSignalAddon()
        content = 'Simple content'
        context = {}
        result = addon.evaluate(content, context)
        self.assertIsInstance(result, SignalResult)
        self.assertEqual(result.addon_id, 'humor_signal_addon')
        self.assertIsInstance(result.score, float)
        self.assertIsInstance(result.confidence, float)
        dimensions = result.metadata['dimensions']
        self.assertEqual(len(dimensions), 7)
        for dim_value in dimensions.values():
            self.assertIsInstance(dim_value, float)
            self.assertGreaterEqual(dim_value, 0.0)
            self.assertLessEqual(dim_value, 1.0)

    def test_addon_info(self):
        """Test that addon info is correctly provided."""
        addon = HumorSignalAddon()
        info = addon.get_addon_info()
        self.assertIsInstance(info, dict)
        self.assertIn('addon_id', info)
        self.assertIn('type', info)
        self.assertIn('config', info)
        self.assertEqual(info['addon_id'], 'humor_signal_addon')
        self.assertEqual(info['type'], 'HumorSignalAddon')
        self.assertIsInstance(info['config'], dict)
if __name__ == '__main__':
    unittest.main()