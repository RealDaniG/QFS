"""
Session Model - v20 Schema Freeze
Deterministic session identity and lifecycle management.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class Session:
    """
    v20 Session Schema (FROZEN - Do not modify fields)
    """

    session_id: str
    subject_ids: Dict[str, Optional[str]]  # {wallet, oidc?, mockpqc?}
    device_id: str
    roles: List[str]
    scopes: List[str]
    issued_at: int  # Unix timestamp
    expires_at: int
    refresh_index: int
    session_schema_version: int = 1
    mfa_level: str = "none"  # Placeholder for v20
    device_trust_level: str = "unknown"  # Placeholder for v20

    def is_expired(self, current_time: int) -> bool:
        """Check if session is expired."""
        return current_time >= self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for EvidenceBus."""
        return {
            "session_schema_version": self.session_schema_version,
            "session_id": self.session_id,
            "subject_ids": self.subject_ids,
            "device_id": self.device_id,
            "roles": self.roles,
            "scopes": self.scopes,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "refresh_index": self.refresh_index,
            "mfa_level": self.mfa_level,
            "device_trust_level": self.device_trust_level,
        }
