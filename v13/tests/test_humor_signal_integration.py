"""
Tests for the humor signal addon integration with ATLAS API Gateway
"""
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.ATLAS.src.signals.humor import HumorSignalAddon

class TestHumorSignalIntegration:
    """Test suite for humor signal addon integration with ATLAS API Gateway"""

    def setup_method(self):
        """Setup test environment"""
        self.gateway = AtlasAPIGateway()
        self.humor_addon = HumorSignalAddon()

    def test_humor_signal_addon_initialization(self):
        """Test that humor signal addon is properly initialized in gateway"""
        assert hasattr(self.gateway, 'humor_signal_addon')
        assert isinstance(self.gateway.humor_signal_addon, HumorSignalAddon)

    def test_process_humor_signals_success(self):
        """Test successful processing of humor signals"""
        content = "Why don't scientists trust atoms? Because they make up everything!"
        context = {'views': 100, 'laughs': 50, 'saves': 20, 'replays': 30, 'author_reputation': 0.8}
        humor_data = self.gateway._process_humor_signals(content, context)
        assert humor_data is not None
        assert 'dimensions' in humor_data
        assert 'confidence' in humor_data
        assert 'result_hash' in humor_data
        assert 'content_hash' in humor_data
        assert 'context_hash' in humor_data
        dimensions = humor_data['dimensions']
        assert isinstance(dimensions, dict)
        assert len(dimensions) == 7
        expected_dimensions = ['chronos', 'lexicon', 'surreal', 'empathy', 'critique', 'slapstick', 'meta']
        for dim in sorted(expected_dimensions):
            assert dim in dimensions
            assert isinstance(dimensions[dim], float)
            assert 0 <= dimensions[dim] <= 1
        assert isinstance(humor_data['confidence'], float)
        assert 0 <= humor_data['confidence'] <= 1

    def test_process_humor_signals_empty_content(self):
        """Test processing of humor signals with empty content"""
        content = ''
        context = {'views': 0, 'laughs': 0, 'saves': 0, 'replays': 0, 'author_reputation': 0.5}
        humor_data = self.gateway._process_humor_signals(content, context)
        assert humor_data is not None
        assert 'dimensions' in humor_data
        assert 'confidence' in humor_data

    def test_process_humor_signals_exception_handling(self):
        """Test that exceptions in humor signal processing are handled gracefully"""
        content = None
        context = {'views': 100, 'laughs': 50, 'saves': 20, 'replays': 30, 'author_reputation': 0.8}
        humor_data = self.gateway._process_humor_signals(content, context)
        assert humor_data is None
if __name__ == '__main__':
    pytest.main([__file__])