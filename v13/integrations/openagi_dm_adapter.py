"""
openagi_dm_adapter.py - Open-AGI Adapter for Direct Messaging
Routes DM operations through Open-AGI governance surface
"""

from typing import Dict, Any, List, Optional
from v13.services.dm.messenger import DirectMessagingService


class OpenAGIDMAdapter:
    """
    Bridges DM service to Open-AGI tool surface.
    Ensures all DM operations are:
    - Capability-gated
    - AEGIS-guarded
    - Ledger-event-shaped (even in simulation)
    - Explainable
    """

    def __init__(self, dm_service: DirectMessagingService, scope: str = "PRODUCTION"):
        self.dm_service = dm_service
        self.scope = scope

    def dm_create_thread(self, caller_id: str, recipient_id: str) -> Dict[str, Any]:
        """
        Open-AGI tool: Create a new DM thread.
        """
        # Check capability
        if not self._has_capability(caller_id, "DM_CREATE_THREAD"):
            return {
                "error": "UNAUTHORIZED",
                "reason": "Missing DM_CREATE_THREAD capability",
            }

        # Check recipient exists
        recipient = self.dm_service.identity_mgr.get_identity(recipient_id)
        if not recipient:
            return {"error": "RECIPIENT_NOT_FOUND"}

        # Generate thread ID
        thread_id = f"thread_{caller_id}_{recipient_id}"

        # Emit event (ledger-shaped)
        event = {
            "event_type": "DM_THREAD_CREATED",
            "scope": self.scope,
            "creator": caller_id,
            "participants": [caller_id, recipient_id],
            "thread_id": thread_id,
            "timestamp": "deterministic_time",
        }

        if self.scope == "SIMULATION":
            # Don't commit to real ledger
            return {"thread_id": thread_id, "simulated": True, "event": event}
        else:
            # Would emit to real ledger here
            return {"thread_id": thread_id}

    def dm_send_message(
        self,
        caller_id: str,
        thread_id: str,
        content: str,
        storage_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Open-AGI tool: Send a message in a thread.
        Includes AEGIS guard integration.
        """
        # Check capability
        if not self._has_capability(caller_id, "DM_SEND"):
            return {"error": "UNAUTHORIZED"}

        # AEGIS Pre-Check (mock for now)
        if self._is_content_flagged(content):
            return {"error": "CONTENT_FLAGGED", "reason": "Safety policy violation"}

        # Rate limit check (mock)
        if self._is_rate_limited(caller_id):
            return {"error": "RATE_LIMITED"}

        # Mock storage URI if not provided
        if not storage_uri:
            storage_uri = f"sim://msg_{hash(content)}"

        # Generate message ID
        message_id = f"msg_{thread_id}_{len(content)}"

        # Emit event
        event = {
            "event_type": "DM_MESSAGE_SENT",
            "scope": self.scope,
            "sender": caller_id,
            "thread_id": thread_id,
            "message_id": message_id,
            "storage_uri": storage_uri,
            "content_hash": hash(content),
            "timestamp": "deterministic_time",
        }

        if self.scope == "SIMULATION":
            return {"message_id": message_id, "simulated": True, "event": event}
        else:
            # Real send
            success = self.dm_service.send_message_signal(
                caller_id, "recipient", storage_uri, str(hash(content))
            )
            return {"message_id": message_id, "success": success}

    def dm_list_threads(self, caller_id: str) -> Dict[str, Any]:
        """
        Open-AGI tool: List caller's threads.
        """
        if not self._has_capability(caller_id, "DM_READ_OWN"):
            return {"error": "UNAUTHORIZED"}

        # Mock thread list
        threads = [{"thread_id": "thread_1", "participants": [caller_id, "other_user"]}]

        return {"threads": threads}

    def dm_get_message_history(
        self, caller_id: str, thread_id: str, limit: int = 50
    ) -> Dict[str, Any]:
        """
        Open-AGI tool: Get message history for a thread.
        """
        if not self._has_capability(caller_id, "DM_READ_OWN"):
            return {"error": "UNAUTHORIZED"}

        # Check thread membership (mock)
        if not self._is_thread_participant(caller_id, thread_id):
            return {"error": "UNAUTHORIZED", "reason": "Not a thread participant"}

        # Mock message history
        messages = [
            {"message_id": "msg_1", "sender": caller_id, "content_ref": "ipfs://..."}
        ]

        return {"messages": messages[:limit]}

    # Helper methods
    def _has_capability(self, user_id: str, capability: str) -> bool:
        """Check if user has required capability."""
        # Mock: In production, query v13.policy.authorization
        if self.scope == "SIMULATION":
            return capability in [
                "DM_SEND",
                "DM_READ_OWN",
                "DM_CREATE_THREAD",
                "DM_ADMIN_SIMULATE",
            ]
        return True

    def _is_content_flagged(self, content: str) -> bool:
        """AEGIS content safety check."""
        # Mock: In production, call AEGIS guard
        return "unsafe" in content.lower()

    def _is_rate_limited(self, user_id: str) -> bool:
        """Rate limit check."""
        # Mock
        return False

    def _is_thread_participant(self, user_id: str, thread_id: str) -> bool:
        """Check if user is in thread."""
        # Mock
        return True
