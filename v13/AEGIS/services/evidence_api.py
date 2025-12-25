from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..ui_contracts.schemas import ProofVectorRef
from .evidence_service import get_proof_vectors_by_ids
from v13.atlas.src.api.dependencies import get_replay_source
from v13.core.QFSReplaySource import QFSReplaySource

router = APIRouter()


@router.get("/proof_vectors", response_model=List[ProofVectorRef])
async def get_proof_vectors(
    ids: str, replay_source: QFSReplaySource = Depends(get_replay_source)
):
    """
    Get proof vectors by comma-separated IDs.
    Internal endpoint for AEGIS UX components.
    """
    if not ids:
        return []

    id_list = [i.strip() for i in ids.split(",")]
    return get_proof_vectors_by_ids(id_list, replay_source)
