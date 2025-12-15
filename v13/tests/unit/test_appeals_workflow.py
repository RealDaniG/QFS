"""
test_appeals_workflow.py - Unit tests for Appeals Workflow
"""

import pytest
from v13.services.appeals.manager import AppealManager


def test_appeal_submission():
    mgr = AppealManager()

    appeal = mgr.submit_appeal(
        user_id="0xUser",
        target_event_id="event_123",
        evidence_cid="ipfs://Qm123",
        reason="False positive",
    )

    assert appeal["user_id"] == "0xUser"
    assert appeal["status"] == "PENDING"
    assert appeal["decision"] is None


def test_appeal_resolution():
    mgr = AppealManager()

    appeal = mgr.submit_appeal("0xUser", "event_123", "ipfs://Qm123", "...")
    aid = appeal["id"]

    # Resolve
    resolved = mgr.resolve_appeal(aid, "ACCEPTED", "0xCouncil", "ipfs://QmExplanation")

    assert resolved["status"] == "RESOLVED"
    assert resolved["decision"] == "ACCEPTED"
    assert resolved["reviewer"] == "0xCouncil"


def test_invalid_decision():
    mgr = AppealManager()
    appeal = mgr.submit_appeal("0xUser", "event_123", "ipfs://Qm123", "...")

    with pytest.raises(ValueError, match="Invalid decision"):
        mgr.resolve_appeal(appeal["id"], "MAYBE", "0xCouncil", "ipfs://...")


def test_list_pending():
    mgr = AppealManager()

    mgr.submit_appeal("0xUser1", "e1", "cid1", "r1")
    mgr.submit_appeal("0xUser2", "e2", "cid2", "r2")

    pending = mgr.list_pending()
    assert len(pending) == 2

    # Resolve one
    mgr.resolve_appeal(pending[0]["id"], "ACCEPTED", "0xC", "cid")

    pending_after = mgr.list_pending()
    assert len(pending_after) == 1
