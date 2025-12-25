import unittest
from v15.auth.mockpqc import MockPQCProvider


class TestMOCKPQCAuth(unittest.TestCase):
    def test_mockpqc_deterministic_sign(self):
        """Invariant AUTH-P1: MOCKPQC key generation and signing are deterministic."""
        key = MockPQCProvider.generate_key("0xUser", "SEED_REF_1", 1000)

        msg = "Verify me"
        sig1 = MockPQCProvider.sign(key, msg)
        sig2 = MockPQCProvider.sign(key, msg)

        self.assertEqual(sig1, sig2)
        self.assertTrue(MockPQCProvider.verify(key, msg, sig1))
        self.assertFalse(MockPQCProvider.verify(key, msg + "tamper", sig1))

    def test_mockpqc_keys_change_with_seed(self):
        key1 = MockPQCProvider.generate_key("0xUser", "SEED_1", 1000)
        key2 = MockPQCProvider.generate_key("0xUser", "SEED_2", 1000)

        self.assertNotEqual(key1.key_id, key2.key_id)
