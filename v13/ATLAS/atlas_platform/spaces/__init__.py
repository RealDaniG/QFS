"""
ATLAS Spaces Module - Initialization
"""

from .spaces_manager import (
    SpacesManager,
    Space,
    Participant,
    SpaceStatus,
    ParticipantRole,
)
from .spaces_events import (
    emit_space_created,
    emit_space_joined,
    emit_space_spoke,
    emit_space_ended,
)

__all__ = [
    "SpacesManager",
    "Space",
    "Participant",
    "SpaceStatus",
    "ParticipantRole",
    "emit_space_created",
    "emit_space_joined",
    "emit_space_spoke",
    "emit_space_ended",
]
