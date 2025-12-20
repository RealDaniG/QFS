from pathlib import Path
import pytest
from fastapi.testclient import TestClient
_THIS_FILE = Path(__file__).resolve()
_ATLAS_ROOT = None
for parent in sorted(_THIS_FILE.parents):
    if parent.name == 'ATLAS':
        _ATLAS_ROOT = parent
        break
if _ATLAS_ROOT is not None:
    if str(_ATLAS_ROOT) not in sys.path:
        sys.path.insert(0, str(_ATLAS_ROOT))
from src.main import app

@pytest.fixture(scope='module')
def client() -> TestClient:
    return TestClient(app)

def _auth_headers(token: str='test-token') -> dict:
    return {'Authorization': f'Bearer {token}'}

def test_wallets_requires_auth(client: TestClient) -> None:
    response = client.get('/api/v1/wallets/')
    assert response.status_code == 401

def test_wallets_minimal_happy_path(client: TestClient) -> None:
    payload = {'name': 'Primary Wallet', 'description': 'test wallet', 'asset': 'QFS', 'metadata': {'purpose': 'phase-b'}}
    create = client.post('/api/v1/wallets/', json=payload, headers=_auth_headers())
    assert create.status_code == 201
    body = create.json()
    assert 'wallet_id' in body
    assert body['owner_id'] == 'user123'
    assert body['name'] == 'Primary Wallet'
    assert body['is_active'] is True
    assert isinstance(body.get('balances'), list)
    lst = client.get('/api/v1/wallets/', headers=_auth_headers())
    assert lst.status_code == 200
    wallets = lst.json()
    assert isinstance(wallets, list)
    assert any((w.get('wallet_id') == body['wallet_id'] for w in wallets))

def test_wallets_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post('/api/v1/wallets/', json={'description': 'missing name'}, headers=_auth_headers())
    assert response.status_code in (400, 401, 403, 422)
    assert response.status_code != 500
