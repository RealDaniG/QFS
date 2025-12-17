from fastapi import APIRouter, Body
from ..ui_contracts.schemas import SandboxScenarioRequest, SandboxResult
from .engine import run_sandbox_scenario
from .assistant import analyze_sandbox_result

router = APIRouter()


@router.post("/sandbox/run", response_model=SandboxResult)
async def run_scenario(req: SandboxScenarioRequest):
    """
    Run a sandbox scenario and return annotated results.
    """
    # 1. Execute deterministic run
    raw_result = run_sandbox_scenario(req.template_id, req.params, req.user_settings)

    # 2. Helper analysis (Track 5.3)
    final_result = analyze_sandbox_result(raw_result, req.user_settings)

    return final_result
