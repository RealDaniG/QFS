import unittest
import asyncio
from libs.PQC import PQC, KeyPair, ValidationResult
from ATLAS.src.qfs_client import QFSClient
from ATLAS.src.qfs_types import OperationBundle
from unittest.mock import MagicMock


class TestPQCIntegration(unittest.TestCase):
    def test_pqc_backend_info(self):
        info = PQC.get_backend_info()
        print(f"PQC Backend: {info}")
        self.assertIn("backend", info)
        self.assertIn("algorithm", info)
        self.assertIn("production_ready", info)

    def test_keygen_sign_verify_flow(self):
        """Test the full PQC lifecycle with the active backend"""
        seed = b"deterministic_seed_for_testing_123"

        with PQC.LogContext() as log:
            # 1. Keygen
            keypair = PQC.generate_keypair(log, seed=seed)
            self.assertIsInstance(keypair, KeyPair)
            self.assertTrue(len(keypair.public_key) > 0)
            self.assertTrue(len(keypair.private_key) > 0)

            # 2. Sign
            message = {"action": "vote", "target": "proposal_1"}
            signature = PQC.sign_data(keypair.private_key, message, log)
            self.assertTrue(len(signature) > 0)

            # 3. Verify
            result = PQC.verify_signature(keypair.public_key, message, signature, log)
            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.is_valid)

            # 4. Verify with tampered data
            tampered_message = {"action": "vote", "target": "proposal_2"}
            result_tampered = PQC.verify_signature(
                keypair.public_key, tampered_message, signature, log
            )
            self.assertFalse(result_tampered.is_valid)

    def test_qfs_client_pqc_signing(self):
        """Test that QFSClient correctly uses PQC signing"""
        # Create a real keypair first to emulate proper usage
        with PQC.LogContext() as log:
            keypair = PQC.generate_keypair(log, seed=b"client_seed")

        # Mock ledger
        mock_ledger = MagicMock()
        f = asyncio.Future()
        f.set_result({"status": "submitted"})
        mock_ledger.submit_bundle.return_value = f

        # Init client with private key (as hex string, to match typical config usage)
        priv_key_hex = keypair.private_key.hex()
        client = QFSClient(ledger=mock_ledger, private_key=priv_key_hex)

        # Submit transaction
        from ATLAS.src.types import Transaction

        tx = Transaction(
            transaction_id="tx1",
            operation_type="PAYMENT",
            creator_id="user1",
            data={"amount": 100},
            nonce=1,
        )

        asyncio.run(client.submit_transaction(tx))

        # Verify call arguments
        submit_call = mock_ledger.submit_bundle.call_args
        self.assertIsNotNone(submit_call)
        bundle = submit_call[0][0]
        self.assertIsInstance(bundle, OperationBundle)
        self.assertIsNotNone(bundle.signature)
        self.assertTrue(len(bundle.signature) > 0)

        # Verify the signature on the bundle manually
        with PQC.LogContext() as log:
            # signature in bundle is hex string
            sig_bytes = bytes.fromhex(bundle.signature)
            # bundle.to_dict() is what was signed (minus signature field)
            data_to_verify = bundle.to_dict()
            if "signature" in data_to_verify:
                del data_to_verify["signature"]

            is_valid = PQC.verify_signature(
                keypair.public_key, data_to_verify, sig_bytes, log
            ).is_valid
            self.assertTrue(is_valid, "Bundle signature verification failed")


if __name__ == "__main__":
    unittest.main()
