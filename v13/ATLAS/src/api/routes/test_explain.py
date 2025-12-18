"""
Test suite for the explain API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

def test_explain_reward_endpoint():
    """Test that the explain reward endpoint works correctly."""
    from v13.ATLAS.src.api import app
    client = TestClient(app)
    response = client.get('/explain/reward/wallet_123')
    assert response.status_code == 200
    data = response.json()
    assert data['wallet_id'] == 'wallet_123'
    assert 'base' in data
    assert 'bonuses' in data
    assert 'caps' in data
    assert 'guards' in data
    assert 'total' in data
    assert 'metadata' in data

def test_explain_reward_endpoint_with_epoch():
    """Test that the explain reward endpoint works with epoch parameter."""
    from v13.ATLAS.src.api import app
    client = TestClient(app)
    response = client.get('/explain/reward/wallet_456?epoch=2')
    assert response.status_code == 200
    data = response.json()
    assert data['wallet_id'] == 'wallet_456'
    assert data['epoch'] == 2

def test_explain_ranking_endpoint():
    """Test that the explain ranking endpoint works correctly."""
    from v13.ATLAS.src.api import app
    client = TestClient(app)
    response = client.get('/explain/ranking/content_123')
    assert response.status_code == 200
    data = response.json()
    assert data['content_id'] == 'content_123'
    assert 'signals' in data
    assert 'neighbors' in data
    assert 'final_rank' in data
    assert 'metadata' in data
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
