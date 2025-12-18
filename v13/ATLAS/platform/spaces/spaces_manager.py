"""
ATLAS Spaces Module - Live Room Management

Implements deterministic live room functionality for ATLAS social platform.
All operations are Zero-Sim compliant with full replay capability.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

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
    """Space participant with deterministic tracking"""

    wallet_id: str
    joined_at: int  # Deterministic timestamp
    role: ParticipantRole
    speak_duration: int = 0  # Seconds, for reward calculation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wallet_id": self.wallet_id,
            "joined_at": self.joined_at,
            "role": self.role.value,
            "speak_duration": self.speak_duration,
        }


@dataclass
class Space:
    """Live room space with deterministic properties"""

    space_id: str  # Deterministic UUID v5
    host_wallet: str
    title: str
    created_at: int  # Deterministic timestamp
    participants: Dict[str, Participant]  # wallet_id -> Participant
    status: SpaceStatus
    metadata: Dict[str, Any]
    pqc_signature: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "space_id": self.space_id,
            "host_wallet": self.host_wallet,
            "title": self.title,
            "created_at": self.created_at,
            "participants": {k: v.to_dict() for k, v in self.participants.items()},
            "status": self.status.value,
            "metadata": self.metadata,
            "pqc_signature": self.pqc_signature,
        }

    def get_participant_count(self) -> int:
        """Get current participant count"""
        return len(self.participants)

    def is_host(self, wallet_id: str) -> bool:
        """Check if wallet is the host"""
        return wallet_id == self.host_wallet

    def get_participant(self, wallet_id: str) -> Optional[Participant]:
        """Get participant by wallet ID"""
        return self.participants.get(wallet_id)


class SpacesManager:
    """
    Manages ATLAS Spaces (live rooms) with deterministic operations.

    All state changes emit EconomicEvents for QFS integration.
    Zero-Sim compliant: no randomness, full replay capability.
    """

    def __init__(self, cm: CertifiedMath, max_participants: int = 100):
        """
        Initialize SpacesManager.

        Args:
            cm: CertifiedMath instance for deterministic calculations
            max_participants: Maximum participants per space
        """
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
        """
        Create a new space with deterministic ID.

        Args:
            host_wallet: Wallet ID of the host
            title: Space title
            timestamp: Deterministic timestamp from DRV_Packet
            metadata: Optional metadata
            log_list: Optional log list for audit trail

        Returns:
            Space: Created space instance
        """
        if log_list is None:
            log_list = []

        # Generate deterministic space ID (UUID v5 from host + timestamp + title)
        space_data = f"{host_wallet}:{timestamp}:{title}"
        space_id = DeterministicID.from_string(space_data)

        # Create host participant
        host_participant = Participant(
            wallet_id=host_wallet,
            joined_at=timestamp,
            role=ParticipantRole.HOST,
            speak_duration=0,
        )

        # Create space
        space = Space(
            space_id=space_id,
            host_wallet=host_wallet,
            title=title,
            created_at=timestamp,
            participants={host_wallet: host_participant},
            status=SpaceStatus.ACTIVE,
            metadata=metadata or {},
            pqc_signature="",
        )

        # Store in active spaces
        self.active_spaces[space_id] = space

        # Log operation
        log_list.append(
            {
                "operation": "space_created",
                "space_id": space_id,
                "host_wallet": host_wallet,
                "timestamp": timestamp,
                "title": title,
            }
        )

        return space

    def join_space(
        self,
        space_id: str,
        participant_wallet: str,
        timestamp: int,
        role: ParticipantRole = ParticipantRole.LISTENER,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Participant:
        """
        Add participant to a space.

        Args:
            space_id: Space to join
            participant_wallet: Wallet ID of participant
            timestamp: Deterministic timestamp
            role: Participant role (default: LISTENER)
            log_list: Optional log list

        Returns:
            Participant: Created participant instance

        Raises:
            ValueError: If space not found or full
        """
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

        # Create participant
        participant = Participant(
            wallet_id=participant_wallet,
            joined_at=timestamp,
            role=role,
            speak_duration=0,
        )

        # Add to space
        space.participants[participant_wallet] = participant

        # Log operation
        log_list.append(
            {
                "operation": "space_joined",
                "space_id": space_id,
                "participant_wallet": participant_wallet,
                "timestamp": timestamp,
                "role": role.value,
            }
        )

        return participant

    def leave_space(
        self,
        space_id: str,
        participant_wallet: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Remove participant from a space.

        Args:
            space_id: Space to leave
            participant_wallet: Wallet ID of participant
            timestamp: Deterministic timestamp
            log_list: Optional log list

        Raises:
            ValueError: If space or participant not found
        """
        if log_list is None:
            log_list = []

        space = self.active_spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")

        if participant_wallet not in space.participants:
            raise ValueError(f"Participant {participant_wallet} not in space")

        # Cannot leave if you're the host and there are other participants
        if space.is_host(participant_wallet) and space.get_participant_count() > 1:
            raise ValueError("Host cannot leave while others are present")

        # Remove participant
        participant = space.participants.pop(participant_wallet)

        # Log operation
        log_list.append(
            {
                "operation": "space_left",
                "space_id": space_id,
                "participant_wallet": participant_wallet,
                "timestamp": timestamp,
                "speak_duration": participant.speak_duration,
            }
        )

    def end_space(
        self,
        space_id: str,
        host_wallet: str,
        timestamp: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Space:
        """
        End a space (host only).

        Args:
            space_id: Space to end
            host_wallet: Wallet ID of host
            timestamp: Deterministic timestamp
            log_list: Optional log list

        Returns:
            Space: Ended space instance

        Raises:
            ValueError: If space not found or caller not host
        """
        if log_list is None:
            log_list = []

        space = self.active_spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")

        if not space.is_host(host_wallet):
            raise ValueError(f"Only host can end space")

        # Update status
        space.status = SpaceStatus.ENDED

        # Calculate total duration
        duration = timestamp - space.created_at

        # Log operation
        log_list.append(
            {
                "operation": "space_ended",
                "space_id": space_id,
                "host_wallet": host_wallet,
                "timestamp": timestamp,
                "duration": duration,
                "final_participant_count": space.get_participant_count(),
            }
        )

        # Remove from active spaces
        self.active_spaces.pop(space_id)

        return space

    def get_space(self, space_id: str) -> Optional[Space]:
        """Get space by ID"""
        return self.active_spaces.get(space_id)

    def list_active_spaces(self) -> List[Space]:
        """
        List all active spaces.

        Returns deterministic ordering by creation time.
        """
        return sorted(
            self.active_spaces.values(), key=lambda s: (s.created_at, s.space_id)
        )

    def record_speak_time(
        self,
        space_id: str,
        participant_wallet: str,
        duration_seconds: int,
        log_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Record speaking time for reward calculation.

        Args:
            space_id: Space ID
            participant_wallet: Participant wallet
            duration_seconds: Speaking duration in seconds
            log_list: Optional log list
        """
        if log_list is None:
            log_list = []

        space = self.active_spaces.get(space_id)
        if not space:
            raise ValueError(f"Space {space_id} not found")

        participant = space.get_participant(participant_wallet)
        if not participant:
            raise ValueError(f"Participant {participant_wallet} not in space")

        # Update speak duration
        participant.speak_duration += duration_seconds

        # Log operation
        log_list.append(
            {
                "operation": "speak_time_recorded",
                "space_id": space_id,
                "participant_wallet": participant_wallet,
                "duration_seconds": duration_seconds,
                "total_speak_duration": participant.speak_duration,
            }
        )
