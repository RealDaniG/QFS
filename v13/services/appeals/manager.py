"""
manager.py - Appeals Management Service
"""

import uuid
import time
from typing import Dict, Any, Optional, List


class AppealManager:
    """
    Manages the lifecycle of user appeals.
    """

    def __init__(self):
        # In-memory storage for V1
        self._appeals: Dict[str, Dict[str, Any]] = {}

    def submit_appeal(
        self, user_id: str, target_event_id: str, evidence_cid: str, reason: str
    ) -> Dict[str, Any]:
        """
        Submit a new appeal.
        """
        appeal_id = f"appeal_{uuid.uuid4().hex[:12]}"

        appeal = {
            "id": appeal_id,
            "user_id": user_id,
            "target_event_id": target_event_id,
            "evidence_cid": evidence_cid,
            "reason": reason,
            "status": "PENDING",
            "submitted_at": int(time.time()),
            "decision": None,
            "reviewer": None,
        }

        self._appeals[appeal_id] = appeal
        # Emit APPEAL_SUBMITTED event to ledger
        return appeal

    def get_appeal(self, appeal_id: str) -> Optional[Dict[str, Any]]:
        return self._appeals.get(appeal_id)

    def resolve_appeal(
        self, appeal_id: str, decision: str, reviewer: str, explanation_cid: str
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve an appeal.
        decision: "ACCEPTED" | "REJECTED"
        """
        appeal = self._appeals.get(appeal_id)
        if not appeal:
            return None

        if decision not in ["ACCEPTED", "REJECTED"]:
            raise ValueError("Invalid decision")

        appeal["status"] = "RESOLVED"
        appeal["decision"] = decision
        appeal["reviewer"] = reviewer
        appeal["explanation_cid"] = explanation_cid
        appeal["resolved_at"] = int(time.time())

        # Emit APPEAL_RESOLVED event to ledger
        return appeal

    def list_pending(self) -> List[Dict[str, Any]]:
        return [a for a in self._appeals.values() if a["status"] == "PENDING"]
