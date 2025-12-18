"""
ATLAS Spaces Module - Live Room Management

Minimal implementation for test validation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

try:
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
    from ...libs.deterministic_helpers import DeterministicID
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.deterministic_helpers import DeterministicID


class SpaceStatus(Enum):
    """Space lifecycle status"""

    ACTIVE = "active"
    ENDED = "ended"
    PAUSED = "paused"


class ParticipantRole(Enum):
    """Participant roles in a space"""

    HOST = "host"
    SPEAKER = "speaker"
    LISTENER = "listener"


@dataclass
class Participant:
    """Space participant"""

    wallet_id: str
    joined_at: int
    role: ParticipantRole
    speak_duration: int = 0


@dataclass
class Space:
    """Live room space"""

    space_id: str
    host_wallet: str
    title: str
    created_at: int
    participants: Dict[str, Participant] = field(default_factory=dict)
    status: SpaceStatus = SpaceStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    pqc_signature: str = ""

    def get_participant_count(self) -> int:
        return len(self.participants)

    def is_host(self, wallet_id: str) -> bool:
        return wallet_id == self.host_wallet

    def get_participant(self, wallet_id: str) -> Optional[Participant]:
        return self.participants.get(wallet_id)


class SpacesManager:
    """Manages ATLAS Spaces"""

    def __init__(self, cm: CertifiedMath, max_participants: int = 100):
        self.cm = cm
        self.max_participants = max_participants
        self.active_spaces: Dict[str, Space] = {}

    def create_space(
        self,
        host_wallet: str,
        title: str,
        timestamp: int,
        metadata: Optional[Dict[str, Any]] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Space:
        if log_list is None:
            log_list = []

        space_data = f"{host_wallet}:{timestamp}:{title}"
        space_id = DeterministicID.from_string(space_data)

        host_participant = Participant(
            wallet_id=host_wallet, joined_at=timestamp, role=ParticipantRole.HOST
        )

        space = Space(
            space_id=space_id,
            host_wallet=host_wallet,
            title=title,
            created_at=timestamp,
            participants={host_wallet: host_participant},
            status=SpaceStatus.ACTIVE,
            metadata=metadata or {},
        )

        self.active_spaces[space_id] = space
        log_list.append({"operation": "space_created", "space_id": space_id})
        return space

    def join_space(
        self,
        space_id: str,
        participant_wallet: str,
        timestamp: int,
        role: ParticipantRole = ParticipantRole.LISTENER,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Participant:
        if log_list is None:
            log_list = []

        space = self.active_spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")
        if space.status != SpaceStatus.ACTIVE:
            raise ValueError(f"Space {space_id} is not active")
        if space.get_participant_count() >= self.max_participants:
            raise ValueError(f"Space {space_id} is full")
        if participant_wallet in space.participants:
            raise ValueError(f"Participant {participant_wallet} already in space")

        participant = Participant(
            wallet_id=participant_wallet, joined_at=timestamp, role=role
        )

        space.participants[participant_wallet] = participant
        log_list.append({"operation": "space_joined", "space_id": space_id})
        return participant

    def leave_space(
        self,
        space_id: str,
        participant_wallet: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if log_list is None:
            log_list = []

        space = self.active_spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")
        if participant_wallet not in space.participants:
            raise ValueError(f"Participant {participant_wallet} not in space")
        if space.is_host(participant_wallet) and space.get_participant_count() > 1:
            raise ValueError("Host cannot leave while others are present")

        space.participants.pop(participant_wallet)
        log_list.append({"operation": "space_left", "space_id": space_id})

    def end_space(
        self,
        space_id: str,
        host_wallet: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Space:
        if log_list is None:
            log_list = []

        space = self.active_spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")
        if not space.is_host(host_wallet):
            raise ValueError("Only host can end space")

        space.status = SpaceStatus.ENDED
        log_list.append({"operation": "space_ended", "space_id": space_id})
        self.active_spaces.pop(space_id)
        return space

    def record_speak_time(
        self,
        space_id: str,
        participant_wallet: str,
        duration_seconds: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if log_list is None:
            log_list = []

        space = self.active_spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")

        participant = space.get_participant(participant_wallet)
        if not participant:
            raise ValueError(f"Participant {participant_wallet} not in space")

        participant.speak_duration += duration_seconds
        log_list.append({"operation": "speak_time_recorded", "space_id": space_id})

    def list_active_spaces(self) -> List[Space]:
        return sorted(
            self.active_spaces.values(), key=lambda s: (s.created_at, s.space_id)
        )
