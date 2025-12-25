import unittest
import time
from v15.auth.session import Session


class TestSessionModel(unittest.TestCase):
    def test_session_required_fields(self):
        """Invariant AUTH-S1: Session schema complete and v1 frozen."""
        now = int(time.time())
        session = Session(
            session_id="test_sess_123",
            subject_ids={"wallet": "0x123"},
            device_id="dev_hash_abc",
            roles=["user"],
            scopes=["read"],
            issued_at=now,
            expires_at=now + 3600,
            refresh_index=0,
        )

        # Verify schema version
        self.assertEqual(session.session_schema_version, 1)

        # Verify serialization
        data = session.to_dict()
        self.assertIn("session_schema_version", data)
        self.assertEqual(data["session_id"], "test_sess_123")
        self.assertEqual(data["mfa_level"], "none")  # Default check

    def test_session_expiry(self):
        now = int(time.time())
        session = Session(
            session_id="s1",
            subject_ids={},
            device_id="d1",
            roles=[],
            scopes=[],
            issued_at=now,
            expires_at=now + 100,
            refresh_index=0,
        )

        self.assertFalse(session.is_expired(now))
        self.assertTrue(session.is_expired(now + 101))
