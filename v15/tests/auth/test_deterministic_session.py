import unittest
from v15.auth.session_id import SessionIDGenerator


class TestDeterministicSession(unittest.TestCase):
    def test_deterministic_session_id(self):
        """Invariant AUTH-S2: Session ID is deterministic."""
        seed = "NODE_TEST_SEED_v1"
        gen = SessionIDGenerator(seed)

        sid1 = gen.generate("0xUser1", 1700000000)

        # Re-create generator (simulation replay)
        gen2 = SessionIDGenerator(seed)
        sid2 = gen2.generate("0xUser1", 1700000000)

        self.assertEqual(
            sid1, sid2, "Session ID must be deterministic given same seed/inputs"
        )

    def test_session_id_collision_resistance(self):
        """Verify inputs change output."""
        gen = SessionIDGenerator("seed")
        sid1 = gen.generate("0xUser1", 100)
        sid2 = gen.generate("0xUser1", 100)  # Counter increments

        self.assertNotEqual(sid1, sid2)

        # Check counter
        self.assertEqual(gen.get_counter(), 2)
