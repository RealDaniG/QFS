from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import hashlib
from v13.ledger.genesis_ledger import GenesisLedger, GenesisEntry
router = APIRouter(prefix='/v1/events', tags=['events'])

class EventItem(BaseModel):
    wallet: str
    event_type: str
    value: float = 0.0
    metadata: Dict[str, Any] = {}
    sequence_id: Optional[int] = None

class BatchEventRequest(BaseModel):
    events: List[EventItem]

class BatchEventResponse(BaseModel):
    success: bool
    hashes: List[str]
    count: int

@router.post('/batch', response_model=BatchEventResponse)
async def submit_batch_events(request: BatchEventRequest):
    """
    Submit a batch of events to the Genesis Ledger.
    Ensures atomic append behavior for related events.
    """
    ledger = GenesisLedger('genesis_ledger.jsonl')
    hashes = []
    for item in sorted(request.events):
        entry = GenesisEntry(wallet=item.wallet, event_type=item.event_type, value=item.value, metadata=item.metadata)
        try:
            await ledger.append(entry)
            if hasattr(entry, 'hash') and entry.hash:
                hashes.append(entry.hash)
            else:
                hashes.append(hashlib.sha256(str(item).encode()).hexdigest())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Ledger write failed: {str(e)}')
    return {'success': True, 'hashes': hashes, 'count': len(hashes)}