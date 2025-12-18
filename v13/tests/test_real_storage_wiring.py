"""
Tests for real storage/IPFS wiring
"""
import pytest
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import FeedRequest
from v13.libs.CertifiedMath import BigNum128

class FakeStorageClient:
    """Fake storage client for testing"""

    def __init__(self):
        self.query_count = 0
        self.get_metadata_count = 0

    def query_feed_candidates(self, user_id, limit):
        """Return fake content IDs"""
        self.query_count += 1
        return [f'content_{i}' for i in range(min(limit, 3))]

    def get_content_metadata(self, content_id):
        """Return fake metadata for content"""
        self.get_metadata_count += 1
        return {'author_did': f'did:user:test_user', 'community_id': 'test_community', 'tags': ['tag1', 'tag2'], 'engagement_signals': {'likes': BigNum128.from_int(100), 'comments': BigNum128.from_int(50), 'shares': BigNum128.from_int(25)}, 'content_cid': f'Qm{hash(content_id):040d}', 'created_at': 1234567890, 'content_type': 'post'}

class FakeIPFSClient:
    """Fake IPFS client for testing"""

    def __init__(self):
        self.get_content_count = 0

    def get_content(self, content_cid):
        """Return fake content text"""
        self.get_content_count += 1
        return f'This is real content from IPFS with CID {content_cid}'

class TestRealStorageWiring:
    """Test suite for real storage/IPFS wiring"""

    def test_storage_ipfs_wiring(self):
        """Test that setting storage/IPFS clients changes behavior"""
        gateway = AtlasAPIGateway()
        mock_candidates = gateway._fetch_content_candidates('test_user', 5)
        assert len(mock_candidates) == 5
        assert mock_candidates[0]['content_id'] == 'cid_test_user_0'
        fake_storage = FakeStorageClient()
        fake_ipfs = FakeIPFSClient()
        gateway.set_storage_clients(fake_storage, fake_ipfs)
        real_candidates = gateway._fetch_content_candidates('test_user', 5)
        assert fake_storage.query_count == 1
        assert fake_storage.get_metadata_count == 3
        assert fake_ipfs.get_content_count == 3
        assert len(real_candidates) == 3
        assert real_candidates[0]['content_id'] == 'content_0'
        assert 'real content from ipfs' in real_candidates[0]['content'].lower()
        assert real_candidates[0]['author_did'] == 'did:user:test_user'

    def test_storage_ipfs_fallback(self):
        """Test that gateway falls back to mock when storage/IPFS fails"""
        gateway = AtlasAPIGateway()

        class FailingStorageClient:

            def query_feed_candidates(self, user_id, limit):
                raise Exception('Storage unavailable')

            def get_content_metadata(self, content_id):
                raise Exception('Storage unavailable')

        class FailingIPFSClient:

            def get_content(self, content_cid):
                raise Exception('IPFS unavailable')
        failing_storage = FailingStorageClient()
        failing_ipfs = FailingIPFSClient()
        gateway.set_storage_clients(failing_storage, failing_ipfs)
        candidates = gateway._fetch_content_candidates('test_user', 5)
        assert len(candidates) == 5
        assert candidates[0]['content_id'] == 'cid_test_user_0'

    def test_feed_with_real_storage(self):
        """Test that get_feed works with real storage/IPFS clients"""
        gateway = AtlasAPIGateway()
        fake_storage = FakeStorageClient()
        fake_ipfs = FakeIPFSClient()
        gateway.set_storage_clients(fake_storage, fake_ipfs)
        request = FeedRequest(user_id='test_user', limit=3, mode='personalized')
        response = gateway.get_feed(request)
        assert response.posts is not None
        assert len(response.posts) <= 3
        assert response.policy_metadata is not None
        assert response.policy_metadata['status'] == 'SUCCESS'
if __name__ == '__main__':
    pytest.main([__file__])
