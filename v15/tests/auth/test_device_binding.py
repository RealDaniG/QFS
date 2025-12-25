import unittest
from v15.auth.device import compute_device_hash


class TestDeviceBinding(unittest.TestCase):
    def test_device_hash_deterministic(self):
        """Invariant AUTH-D1: Device hash is deterministic."""
        h1 = compute_device_hash("Windows", "x86_64", "uuid-123")
        h2 = compute_device_hash("windows ", " X86_64", "uuid-123\n")

        self.assertEqual(h1, h2, "Device hash should normalize inputs")
        self.assertEqual(len(h1), 64)  # SHA3-256 hex

    def test_device_hash_sensitivity(self):
        h1 = compute_device_hash("Windows", "x86_64", "uuid-1")
        h2 = compute_device_hash("Windows", "x86_64", "uuid-2")
        self.assertNotEqual(h1, h2)
