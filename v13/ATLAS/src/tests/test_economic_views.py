from pathlib import Path
_THIS_FILE = Path(__file__).resolve()
_ATLAS_ROOT = None
for parent in _THIS_FILE.parents:
    if parent.name == 'ATLAS':
        _ATLAS_ROOT = parent
        break
if _ATLAS_ROOT is not None:
    if str(_ATLAS_ROOT) not in sys.path:
        sys.path.insert(0, str(_ATLAS_ROOT))
from src.core.economic_views import build_transaction_list_view, build_wallet_summary_view

def test_build_wallet_summary_view_deterministic() -> None:
    payload = {'balance': 10.0, 'locked': 2.0, 'total': 12.0}
    v1 = build_wallet_summary_view(payload, did='did:test', asset='QFS')
    v2 = build_wallet_summary_view(payload, did='did:test', asset='QFS')
    assert v1 == v2
    assert v1.total == 12.0

def test_build_wallet_summary_view_total_fallback() -> None:
    payload = {'balance': 3.5, 'locked': 1.5}
    v = build_wallet_summary_view(payload, did='did:test', asset='QFS')
    assert v.available == 3.5
    assert v.locked == 1.5
    assert v.total == 5.0

def test_build_transaction_list_view_pure_mapping() -> None:
    txs = [{'tx_id': 'tx1', 'sender': 'a', 'receiver': 'b', 'amount': 1.0, 'asset': 'QFS', 'timestamp': '2025-01-01T00:00:00Z', 'status': 'pending'}, {'tx_id': 'tx2', 'sender': 'b', 'receiver': 'a', 'amount': 2.0, 'asset': 'QFS', 'timestamp': '2025-01-01T00:00:01Z', 'status': 'confirmed'}]
    v1 = build_transaction_list_view(txs)
    v2 = build_transaction_list_view(txs)
    assert v1 == v2
    assert v1[0].tx_id == 'tx1'
    assert v1[1].status == 'confirmed'