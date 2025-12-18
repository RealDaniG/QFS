"""
Tests for TokenStateBundle storage metrics extension
"""
import pytest
from v13.core.TokenStateBundle import create_token_state_bundle, TokenStateBundle
from v13.core.StorageEngine import StorageEngine
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

class TestTokenStateBundleStorageExtension:
    """Test suite for TokenStateBundle storage metrics extension"""

    def setup_method(self):
        """Set up test fixtures"""
        self.cm = None

    def test_create_token_state_bundle_with_storage_metrics(self):
        """Test creating TokenStateBundle with storage metrics"""
        chr_state = {'test': 'chr'}
        flx_state = {'test': 'flx'}
        psi_sync_state = {'test': 'psi'}
        atr_state = {'test': 'atr'}
        res_state = {'test': 'res'}
        nod_state = {'test': 'nod'}
        storage_metrics = {'storage_bytes_stored': {'node1': BigNum128.from_int(1000)}, 'storage_uptime_bucket': {'node1': 5}, 'storage_proofs_verified': {'node1': 10}}
        lambda1 = BigNum128.from_int(1)
        lambda2 = BigNum128.from_int(1)
        c_crit = BigNum128.from_int(1)
        pqc_cid = 'test_cid'
        timestamp = 1234567890
        bundle = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, nod_state, lambda1, lambda2, c_crit, pqc_cid, timestamp, storage_metrics)
        assert bundle.storage_metrics == storage_metrics
        assert bundle.storage_metrics['storage_bytes_stored']['node1'].value == 1000000000000000000000
        assert bundle.storage_metrics['storage_uptime_bucket']['node1'] == 5
        assert bundle.storage_metrics['storage_proofs_verified']['node1'] == 10

    def test_create_token_state_bundle_without_storage_metrics(self):
        """Test creating TokenStateBundle without storage metrics (should use defaults)"""
        chr_state = {'test': 'chr'}
        flx_state = {'test': 'flx'}
        psi_sync_state = {'test': 'psi'}
        atr_state = {'test': 'atr'}
        res_state = {'test': 'res'}
        nod_state = {'test': 'nod'}
        lambda1 = BigNum128.from_int(1)
        lambda2 = BigNum128.from_int(1)
        c_crit = BigNum128.from_int(1)
        pqc_cid = 'test_cid'
        timestamp = 1234567890
        bundle = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, nod_state, lambda1, lambda2, c_crit, pqc_cid, timestamp)
        assert 'storage_bytes_stored' in bundle.storage_metrics
        assert 'storage_uptime_bucket' in bundle.storage_metrics
        assert 'storage_proofs_verified' in bundle.storage_metrics
        assert bundle.storage_metrics['storage_bytes_stored'] == {}
        assert bundle.storage_metrics['storage_uptime_bucket'] == {}
        assert bundle.storage_metrics['storage_proofs_verified'] == {}

class TestStorageEngineTokenBundleIntegration:
    """Test suite for StorageEngine TokenStateBundle integration"""

    def setup_method(self):
        """Set up test fixtures"""
        from v13.libs.CertifiedMath import CertifiedMath
        self.cm = CertifiedMath()
        self.storage_engine = StorageEngine(self.cm)
        self.storage_engine.register_storage_node('node1', '192.168.1.1', 8080)
        self.storage_engine.register_storage_node('node2', '192.168.1.2', 8080)
        self.storage_engine.nodes['node1'].bytes_stored = BigNum128.from_int(1000)
        self.storage_engine.nodes['node1'].uptime_bucket = 5
        self.storage_engine.nodes['node1'].proofs_verified = 10
        self.storage_engine.nodes['node2'].bytes_stored = BigNum128.from_int(2000)
        self.storage_engine.nodes['node2'].uptime_bucket = 8
        self.storage_engine.nodes['node2'].proofs_verified = 15

    def test_update_storage_metrics_in_token_bundle(self):
        """Test updating storage metrics in TokenStateBundle"""
        initial_storage_metrics = {'storage_bytes_stored': {'node3': BigNum128.from_int(500)}, 'storage_uptime_bucket': {'node3': 3}, 'storage_proofs_verified': {'node3': 5}}
        initial_bundle = create_token_state_bundle(chr_state={'test': 'chr'}, flx_state={'test': 'flx'}, psi_sync_state={'test': 'psi'}, atr_state={'test': 'atr'}, res_state={'test': 'res'}, nod_state={'test': 'nod'}, lambda1=BigNum128.from_int(1), lambda2=BigNum128.from_int(1), c_crit=BigNum128.from_int(1), pqc_cid='test_cid', timestamp=1234567890, storage_metrics=initial_storage_metrics)
        updated_bundle = self.storage_engine.update_storage_metrics_in_token_bundle(initial_bundle)
        assert updated_bundle.storage_metrics['storage_bytes_stored']['node1'].value == 1000000000000000000000
        assert updated_bundle.storage_metrics['storage_uptime_bucket']['node1'] == 5
        assert updated_bundle.storage_metrics['storage_proofs_verified']['node1'] == 10
        assert updated_bundle.storage_metrics['storage_bytes_stored']['node2'].value == 2000000000000000000000
        assert updated_bundle.storage_metrics['storage_uptime_bucket']['node2'] == 8
        assert updated_bundle.storage_metrics['storage_proofs_verified']['node2'] == 15
        assert updated_bundle.storage_metrics['storage_bytes_stored']['node3'].value == 500000000000000000000
        assert updated_bundle.storage_metrics['storage_uptime_bucket']['node3'] == 3
        assert updated_bundle.storage_metrics['storage_proofs_verified']['node3'] == 5

class TestOpenAGIScoring:
    """Test suite for OpenAGI scoring functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        from v13.libs.CertifiedMath import CertifiedMath
        self.cm = CertifiedMath()
        self.storage_engine = StorageEngine(self.cm)
        self.storage_engine.register_storage_node('node1', '192.168.1.1', 8080)
        self.storage_engine.register_storage_node('node2', '192.168.1.2', 8080)

    def test_openagi_content_scoring(self):
        """Test OpenAGI content scoring"""
        object_id = 'test_object'
        version = 1
        content = b'This is test content for OpenAGI scoring'
        metadata = {'author': 'test_user', 'category': 'test'}
        self.storage_engine.put_content(object_id, version, content, metadata, 1234567890)
        score = self.storage_engine.score_content(object_id, version)
        assert hasattr(score, 'value')
        actual_score = score.value // BigNum128.SCALE
        assert 0 <= actual_score <= 1000000
        score2 = self.storage_engine.score_content(object_id, version)
        assert score.value == score2.value

    def test_openagi_content_scoring_different_content(self):
        """Test that different content produces different scores"""
        object_id1 = 'test_object_1'
        version1 = 1
        content1 = b'First test content'
        metadata1 = {'author': 'test_user'}
        self.storage_engine.put_content(object_id1, version1, content1, metadata1, 1234567891)
        object_id2 = 'test_object_2'
        version2 = 1
        content2 = b'Second test content'
        metadata2 = {'author': 'test_user'}
        self.storage_engine.put_content(object_id2, version2, content2, metadata2, 1234567892)
        score1 = self.storage_engine.score_content(object_id1, version1)
        score2 = self.storage_engine.score_content(object_id2, version2)
        assert score1 != score2 or content1 == content2

    def test_put_content_with_scoring(self):
        """Test storing content with automatic scoring"""
        object_id = 'test_object_with_scoring'
        version = 1
        content = b'Content with automatic OpenAGI scoring'
        metadata = {'author': 'test_user', 'tags': ['scoring', 'test']}
        result = self.storage_engine.put_content_with_scoring(object_id, version, content, metadata, 'default', 1234567893)
        assert 'openagi_score' in result
        assert hasattr(result['openagi_score'], 'value')
        actual_score = result['openagi_score'].value // BigNum128.SCALE
        assert 0 <= actual_score <= 1000000
        object_key = f'{object_id}:{version}'
        assert object_key in self.storage_engine.objects
        assert 'openagi_score' in self.storage_engine.objects[object_key].metadata
        metadata_score = self.storage_engine.objects[object_key].metadata['openagi_score'].value // BigNum128.SCALE
        result_score = result['openagi_score'].value // BigNum128.SCALE
        assert metadata_score == result_score
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
