"""
Auth Event Schemas for EvidenceBus
All events versioned with auth_event_version = 1
"""

from typing import Dict, Any
from datetime import datetime

AUTH_EVENT_VERSION = 1


def create_session_created_event(
    session_id: str,
    wallet_address: str,
    device_hash: str,
    issued_at: int,
    expires_at: int,
) -> Dict[str, Any]:
    """
    SESSION_CREATED event schema.

    Returns:
        Event dict ready for EvidenceBus
    """
    return {
        "event_type": "SESSION_CREATED",
        "auth_event_version": AUTH_EVENT_VERSION,
        "session_id": session_id,
        "wallet": wallet_address,
        "device_hash": device_hash,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "timestamp": int(datetime.utcnow().timestamp()),
    }


def create_session_refreshed_event(
    session_id: str, refresh_index: int, device_hash: str
) -> Dict[str, Any]:
    """
    SESSION_REFRESHED event schema.
    """
    return {
        "event_type": "SESSION_REFRESHED",
        "auth_event_version": AUTH_EVENT_VERSION,
        "session_id": session_id,
        "refresh_index": refresh_index,
        "device_hash": device_hash,
        "timestamp": int(datetime.utcnow().timestamp()),
    }


def create_session_revoked_event(session_id: str, reason: str) -> Dict[str, Any]:
    """
    SESSION_REVOKED event schema.
    """
    return {
        "event_type": "SESSION_REVOKED",
        "auth_event_version": AUTH_EVENT_VERSION,
        "session_id": session_id,
        "reason": reason,
        "timestamp": int(datetime.utcnow().timestamp()),
    }


def create_device_bound_event(session_id: str, device_hash: str) -> Dict[str, Any]:
    """
    DEVICE_BOUND event schema.
    """
    return {
        "event_type": "DEVICE_BOUND",
        "auth_event_version": AUTH_EVENT_VERSION,
        "session_id": session_id,
        "device_hash": device_hash,
        "timestamp": int(datetime.utcnow().timestamp()),
    }


def create_device_mismatch_event(
    session_id: str, expected_device_hash: str, actual_device_hash: str
) -> Dict[str, Any]:
    """
    DEVICE_MISMATCH event schema.
    """
    return {
        "event_type": "DEVICE_MISMATCH",
        "auth_event_version": AUTH_EVENT_VERSION,
        "session_id": session_id,
        "expected_device_hash": expected_device_hash,
        "actual_device_hash": actual_device_hash,
        "timestamp": int(datetime.utcnow().timestamp()),
    }


def create_identity_link_event(
    session_id: str, platform: str, external_id: str, external_handle: str, proof: str
) -> Dict[str, Any]:
    """
    IDENTITY_LINK_PLATFORM event schema.
    Used for GitHub, Discord, etc.
    """
    return {
        "event_type": f"IDENTITY_LINK_{platform.upper()}",
        "auth_event_version": AUTH_EVENT_VERSION,
        "session_id": session_id,
        "platform": platform,
        "external_id": external_id,
        "external_handle": external_handle,
        "proof": proof,
        "timestamp": int(datetime.utcnow().timestamp()),
    }
