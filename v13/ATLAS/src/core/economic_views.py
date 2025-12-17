from __future__ import annotations
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, det_time_isoformat, qnum
from libs.economics.QAmount import QAmount
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

@dataclass(frozen=True)
class WalletSummaryView:
    did: str
    asset: str
    available: QAmount
    locked: QAmount
    total: QAmount

@dataclass(frozen=True)
class TransactionListItemView:
    tx_id: str
    sender: str
    receiver: str
    amount: QAmount
    asset: str
    timestamp: str
    status: str

def build_wallet_summary_view(balance_payload: Mapping[str, Any], *, did: str, asset: str='QFS') -> WalletSummaryView:
    """Pure read-only mapping from a replayable payload to a UI view model.

    This function is intentionally side-effect-free:
    - It does not write to any ledger/state.
    - It does not call time/random.
    - It only maps existing values into a stable view shape.
    """
    available = qnum(balance_payload.get('balance', 0))
    locked = qnum(balance_payload.get('locked', 0))
    total = qnum(balance_payload.get('total', available + locked))
    return WalletSummaryView(did=did, asset=asset, available=available, locked=locked, total=total)

def build_transaction_list_view(transactions: Sequence[Mapping[str, Any]]) -> List[TransactionListItemView]:
    """Pure read-only mapping for transaction responses into UI list items."""
    result: List[TransactionListItemView] = []
    for tx in sorted(transactions):
        result.append(TransactionListItemView(tx_id=str(tx.get('tx_id', '')), sender=str(tx.get('sender', '')), receiver=str(tx.get('receiver', '')), amount=qnum(tx.get('amount', 0)), asset=str(tx.get('asset', 'QFS')), timestamp=str(tx.get('timestamp', '')), status=str(tx.get('status', ''))))
    return result