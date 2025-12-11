import unittest
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Mock PQC library BEFORE importing modules that depend on it
mock_pqc = MagicMock()
sys.modules["src.libs.PQC"] = mock_pqc
sys.modules["pqcrystals"] = MagicMock()
sys.modules["pqcrystals.dilithium"] = MagicMock()

from src.libs.economics.TreasuryDistributionEngine import TreasuryDistributionEngine, create_treasury_distribution_engine
from src.libs.BigNum128 import BigNum128

class MockCertifiedMath:
    def mul(self, a, b, log_list=None):
        val_a = a.value if isinstance(a, BigNum128) else a
        val_b = b.value if isinstance(b, BigNum128) else b
        # Fixed-point multiplication: (a * b) / SCALE
        raw_result = (val_a * val_b) // BigNum128.SCALE
        return BigNum128(raw_result)

    def div_floor(self, a, b, log_list=None):
        val_a = a.value if isinstance(a, BigNum128) else a
        val_b = b.value if isinstance(b, BigNum128) else b
        if val_b == 0: raise ZeroDivisionError()
        return BigNum128.from_int(val_a // val_b)

    def add(self, a, b, log_list=None):
        val_a = a.value if isinstance(a, BigNum128) else a
        val_b = b.value if isinstance(b, BigNum128) else b
        return BigNum128(val_a + val_b)

    def sub(self, a, b, log_list=None):
        val_a = a.value if isinstance(a, BigNum128) else a
        val_b = b.value if isinstance(b, BigNum128) else b
        return BigNum128(val_a - val_b)

class TestTreasuryProportionalDistribution(unittest.TestCase):
    def setUp(self):
        self.math = MockCertifiedMath()
        self.pqc_signer = MagicMock()
        self.pqc_signer.sign.return_value = "mock_signature"
        self.cir302 = MagicMock()
        self.engine = create_treasury_distribution_engine(
            self.math, self.pqc_signer, self.cir302, MagicMock(), MagicMock()
        )

    def test_proportional_distribution(self):
        # Setup
        harmonic_state = MagicMock()
        harmonic_state.node_metrics = {
            "shard_A": {"uptime": 100}, # Score 200
            "shard_B": {"uptime": 300}  # Score 400
        }
        genesis_shards = ["shard_A", "shard_B"]
        treasury_balance = BigNum128.from_int(6000)
        timestamp = 1234567890
        packet_seq = {"seq": 1, "packet_hash": "abc", "pqc_cid": "cid"}

        # Execute
        result = self.engine.compute_system_treasury_distribution(
            harmonic_state, treasury_balance, genesis_shards, timestamp, packet_seq
        )

        # Verify
        dist_map = result["distribution_map"]
        # Total score = 200 + 400 = 600
        # A: 200/600 * 6000 = 2000
        # B: 400/600 * 6000 = 4000
        self.assertEqual(dist_map["shard_A"], "2000.0")
        self.assertEqual(dist_map["shard_B"], "4000.0")
        self.assertEqual(result["total_payout"], "6000.0")
        self.assertEqual(result["remaining_balance"], "0.0")
        
        # Verify PQC signing
        self.pqc_signer.sign.assert_called_once()
        self.assertEqual(result["pqc_signature"], "mock_signature")

    def test_idempotency(self):
        harmonic_state = MagicMock()
        genesis_shards = ["shard_A"]
        treasury_balance = 1000
        timestamp = 100
        packet_seq = 50

        # First run
        res1 = self.engine.compute_system_treasury_distribution(
            harmonic_state, treasury_balance, genesis_shards, timestamp, packet_seq
        )
        self.assertIn("distribution_map", res1)

        # Second run (same seq)
        res2 = self.engine.compute_system_treasury_distribution(
            harmonic_state, treasury_balance, genesis_shards, timestamp, packet_seq
        )
        self.assertEqual(res2["status"], "IDEMPOTENT_SKIP")

if __name__ == "__main__":
    unittest.main()
