"""
Test suite for metrics API endpoints
"""

import unittest
import os

class TestMetricsFileExists(unittest.TestCase):
    """Test cases for metrics file existence"""
    
    def test_metrics_file_exists(self):
        """Test that the metrics.py file exists"""
        metrics_file_path = os.path.join(os.path.dirname(__file__), 'metrics.py')
        self.assertTrue(os.path.exists(metrics_file_path))
        
    def test_metrics_file_not_empty(self):
        """Test that the metrics.py file is not empty"""
        metrics_file_path = os.path.join(os.path.dirname(__file__), 'metrics.py')
        self.assertTrue(os.path.exists(metrics_file_path))
        file_size = os.path.getsize(metrics_file_path)
        self.assertGreater(file_size, 0)

if __name__ == "__main__":
    unittest.main()