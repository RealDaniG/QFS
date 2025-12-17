from fastapi import APIRouter, HTTPException
from .consequence_graph import build_aegis_consequence_graph, AEGISConsequenceGraph

router = APIRouter()


@router.get("/consequence_graph", response_model=AEGISConsequenceGraph)
async def get_aegis_consequence_graph(model_id: str, version: str):
    """
    Get the deterministic consequence graph for a specific AEGIS model version.
    Shows what UIs and capabilities this model enables.
    """
    try:
        return build_aegis_consequence_graph(model_id, version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
