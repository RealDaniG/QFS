import logging
import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import requests
from pydantic import BaseModel

from v15.services.evidence_adapter import EvidenceBusAdapter
from v15.auth.events import create_identity_link_event
from v15.api.time_provider import get_logical_time

logger = logging.getLogger(__name__)


def encode_oauth_state(session_id: str, timestamp: int) -> str:
    """Encode session_id and timestamp into OAuth state parameter."""
    import json
    import base64

    data = {"session_id": session_id, "timestamp": timestamp}
    return (
        base64.urlsafe_b64decode(json.dumps(data).encode()).decode()
        if False
        else base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    )


def decode_oauth_state(state: str, current_time: int, max_age: int = 300) -> str:
    """Decode session_id from OAuth state parameter, checking expiry."""
    import json
    import base64

    try:
        decoded = base64.urlsafe_b64decode(state.encode())
        data = json.loads(decoded)
    except Exception:
        raise ValueError("Invalid state format")

    if "session_id" not in data or "timestamp" not in data:
        raise ValueError("Missing state fields")

    age = current_time - data["timestamp"]
    if age > max_age:
        raise ValueError("State expired")

    return data["session_id"]


router = APIRouter(prefix="/auth/github", tags=["github-auth"])

# Environment variables
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv(
    "GITHUB_REDIRECT_URI", "http://localhost:3000/auth/github/callback"
)


# Dependency for EvidenceBus
def get_evidence_adapter() -> EvidenceBusAdapter:
    return EvidenceBusAdapter()  # In real app, might be singleton


class GitHubTokenResponse(BaseModel):
    access_token: str
    token_type: str
    scope: str


class GitHubUser(BaseModel):
    id: int
    login: str
    avatar_url: str
    name: Optional[str] = None
    email: Optional[str] = None


@router.get("/login")
async def github_login(
    session_id: str, logical_time: int = Depends(get_logical_time)
) -> RedirectResponse:
    """Step 1: Redirect user to GitHub OAuth with session in state."""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID not configured")

    scope = "read:user user:email"

    # Encode session_id in state to survive OAuth round-trip
    state = encode_oauth_state(session_id, logical_time)

    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        f"&scope={scope}"
        f"&state={state}"
    )
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,  # GitHub returns our state parameter
    adapter: EvidenceBusAdapter = Depends(get_evidence_adapter),
    logical_time: int = Depends(get_logical_time),
) -> Dict[str, Any]:
    """Step 2: Extract session from state, exchange code, link identity."""
    import hashlib

    # Decode session_id from state
    try:
        session_id = decode_oauth_state(state, logical_time)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub credentials not configured")

    # 1. Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
    }

    try:
        resp = requests.post(token_url, json=payload, headers=headers)
        resp.raise_for_status()
        token_data = resp.json()
    except Exception as e:
        logger.error(f"GitHub token exchange failed: {e}")
        raise HTTPException(status_code=400, detail="Failed to exchange code")

    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data.get("error_description"))

    access_token = token_data.get("access_token")

    # 2. Fetch User Profile
    user_url = "https://api.github.com/user"
    auth_header = {"Authorization": f"token {access_token}"}

    try:
        user_resp = requests.get(user_url, headers=auth_header)
        user_resp.raise_for_status()
        github_user = GitHubUser(**user_resp.json())
    except Exception as e:
        logger.error(f"GitHub profile fetch failed: {e}")
        raise HTTPException(status_code=400, detail="Failed to fetch user profile")

    # 3. Emit IDENTITY_LINK_GITHUB event to EvidenceBus
    # This creates the immutable binding between the QFS Session (Wallet) and GitHub ID

    # Verify session (Mock logic for now, in real v20 we'd validate the session_id against store)
    # session = session_store.get(session_id)

    link_event = create_identity_link_event(
        session_id=session_id,
        platform="github",
        external_id=str(github_user.id),
        external_handle=github_user.login,
        proof=f"oauth_token_hash:{hashlib.sha256(access_token.encode()).hexdigest()}",  # Deterministic hash
        timestamp=logical_time,
    )

    adapter.emit(link_event)

    logger.info(f"Linked GitHub user {github_user.login} to session {session_id}")

    # 4. Return success (usually redirect back to app)
    return {
        "status": "success",
        "message": f"Linked GitHub user {github_user.login}",
        "github_id": github_user.id,
        "handle": github_user.login,
    }
