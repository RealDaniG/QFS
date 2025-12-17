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

def test_transactions_requires_auth(client: TestClient) -> None:
    response = client.get('/api/v1/transactions/')
    assert response.status_code == 401

def test_transactions_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post('/api/v1/transactions/', json={'receiver': 'user999', 'amount': -1}, headers=_auth_headers())
    assert response.status_code in (400, 401, 403, 422)
    assert response.status_code != 500

def test_transactions_minimal_happy_path(client: TestClient) -> None:
    payload = {'sender': 'ignored_by_server', 'receiver': 'user_456', 'amount': 1.25, 'asset': 'QFS', 'metadata': {'purpose': 'phase-c'}}
    response = client.post('/api/v1/transactions/', json=payload, headers=_auth_headers())
    assert response.status_code == 201
    body = response.json()
    assert 'tx_id' in body
    assert body['receiver'] == 'user_456'
    assert body['amount'] == 1.25
    assert body['asset'] == 'QFS'
    assert body['status'] in ('pending', 'confirmed')

def test_transactions_forbidden_case(client: TestClient) -> None:
    from src.api.routes import transactions as tx_routes
    foreign_tx = tx_routes.transaction_processor.create_transaction(sender='user_other', receiver='user_else', amount=2.0, asset='QFS', metadata={'purpose': 'phase-c-forbidden'})
    tx_routes.transaction_processor.pending_transactions[foreign_tx.tx_id] = foreign_tx
    response = client.get(f'/api/v1/transactions/{foreign_tx.tx_id}', headers=_auth_headers())
    assert response.status_code == 403