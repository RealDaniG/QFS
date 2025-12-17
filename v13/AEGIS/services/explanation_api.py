from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from ..ui_contracts.schemas import UserExplanationSettings, GovernanceMapResponse
from .explanation_control import (
    get_user_settings,
    update_user_settings,
    get_explanation_meta,
)
from .counter_scenario import run_counter_scenario

router = APIRouter()


@router.get("/explanations/settings", response_model=UserExplanationSettings)
async def get_settings(user_id: str = "default_user"):
    return get_user_settings(user_id)


@router.post("/explanations/settings")
async def update_settings(
    settings: UserExplanationSettings, user_id: str = "default_user"
):
    update_user_settings(user_id, settings)
    return {"status": "ok"}


@router.get("/explanations/{explanation_id}/meta")
async def get_meta(explanation_id: str):
    return get_explanation_meta(explanation_id)


@router.post("/explanations/counter_scenario", response_model=GovernanceMapResponse)
async def counter_scenario(
    proposal_id: str = Body(...),
    parameter_overrides: Dict[str, str] = Body(...),
    user_settings: UserExplanationSettings = Body(...),
):
    return run_counter_scenario(proposal_id, parameter_overrides, user_settings)
