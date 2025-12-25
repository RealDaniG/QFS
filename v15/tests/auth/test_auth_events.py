import unittest
from v15.auth import events


class TestAuthEvents(unittest.TestCase):
    def test_auth_event_versioning(self):
        """Invariant AUTH-E1: All events carry version 1."""
        evt = events.create_session_created_event(
            "s1", "w1", "d1", 0, 100, timestamp=1000
        )
        self.assertEqual(evt["auth_event_version"], 1)

    def test_device_bound_event(self):
        evt = events.create_device_bound_event("s1", "h1", timestamp=1000)
        self.assertEqual(evt["event_type"], "DEVICE_BOUND")
        self.assertIn("timestamp", evt)

    def test_session_created_event(self):
        evt = events.create_session_created_event(
            "s1", "w1", "hash", 1, 2, timestamp=1000
        )
        self.assertEqual(evt["wallet"], "w1")
        self.assertEqual(evt["device_hash"], "hash")
