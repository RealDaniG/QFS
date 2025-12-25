import unittest
import base64
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from v13.libs.PQC import PQC, KeyPair, ValidationResult
from v13.atlas.src.core.pqc_session import pqc_session_manager
from v13.atlas.src.qfs_client import QFSClient

# Local definition to avoid importing secure_chat.py which triggers Pydantic recursion in test env
from pydantic import BaseModel


class EstablishRequest(BaseModel):
    wallet_id: str
    kem_ciphertext_b64: str


class TestPQCNetworkIntegration(unittest.TestCase):
    def test_kem_primitives(self):
        """Verify KEM encapsulation and decapsulation correctness."""
        pk, sk = PQC.kem_generate_keypair(PQC.KYBER1024)
        self.assertTrue(len(pk) > 0)
        self.assertTrue(len(sk) > 0)

        # Encapsulate
        ct, ss_sender = PQC.kem_encapsulate(PQC.KYBER1024, pk)
        self.assertTrue(len(ct) > 0)
        self.assertTrue(len(ss_sender) > 0)

        # Decapsulate
        ss_receiver = PQC.kem_decapsulate(PQC.KYBER1024, sk, ct)

        self.assertEqual(ss_sender, ss_receiver, "Shared secrets must match")

    def test_secure_chat_handshake_flow(self):
        """Verify the Secure Chat API Handshake Logic."""
        # 1. Handshake (GET PubKey)
        server_pk = pqc_session_manager.public_key
        server_sk = pqc_session_manager.secret_key

        # Client side simulation
        ct, ss_client = PQC.kem_encapsulate(PQC.KYBER1024, server_pk)
        ct_b64 = base64.b64encode(ct).decode("utf-8")

        # 2. Establish (POST Ciphertext)
        session_id = pqc_session_manager.create_session(ct_b64)
        self.assertIsNotNone(session_id)

        # Verify Server derived same secret
        ss_server = pqc_session_manager.sessions[session_id]
        self.assertEqual(ss_client, ss_server)


class TestConnectionManagerKEM(unittest.TestCase):
    @patch(
        "ATLAS.src.p2p.connection_manager.asyncio.open_connection",
        new_callable=AsyncMock,
    )
    def test_p2p_handshake(self, mock_open_conn):
        """Test the P2P KEM Handshake from Client perspective."""
        # Setup mocks
        mock_reader = AsyncMock()
        mock_writer = MagicMock()
        mock_writer.drain = AsyncMock()  # Make drain awaitable
        mock_writer.wait_closed = AsyncMock()  # Make wait_closed awaitable

        # Mock open_connection (async) returning (reader, writer)
        mock_open_conn.return_value = (mock_reader, mock_writer)

        # Mock Server Response to Hello
        # Server sends: {"node_id": "server_node", "kem_pub_key": "..."}
        server_pk, server_sk = PQC.kem_generate_keypair(PQC.KYBER1024)
        server_pk_b64 = base64.b64encode(server_pk).decode("utf-8")
        server_hello = (
            json.dumps(
                {"node_id": "server_node", "kem_pub_key": server_pk_b64}
            ).encode()
            + b"\n"
        )

        mock_reader.readline.side_effect = [server_hello]

        # Init Manager
        from ATLAS.src.p2p.connection_manager import ConnectionManager

        # Mock bootstrap to assume valid (must be AsyncMock because verify_peer_identity is async)
        mock_bootstrap = MagicMock()
        mock_bootstrap.verify_peer_identity = AsyncMock(return_value=True)

        # Keypair for client (Signing key usually, but for this test irrelevant as client uses Server KEM key)
        # We need a dummy keypair
        priv = b"dummy_priv"
        pub = b"dummy_pub"
        client_kp = KeyPair(priv, pub, "Dilithium5", {})

        mgr = ConnectionManager("client_node", client_kp, mock_bootstrap)

        # Run Connect
        peer_id = asyncio.run(mgr.connect_to_peer("127.0.0.1", 8000))

        self.assertEqual(peer_id, "server_node")

        # Verify Client sent Ciphertext
        # writer.write called with json containing ciphertext
        writes = mock_writer.write.call_args_list
        self.assertTrue(len(writes) > 0)

        # Inspect what was sent
        sent_data = b"".join([call[0][0] for call in writes])
        payload = json.loads(sent_data.decode())
        self.assertEqual(payload["node_id"], "client_node")
        self.assertIn("ciphertext", payload)

        # Verify Ciphertext is valid for Server SK
        ct = base64.b64decode(payload["ciphertext"])
        ss_server = PQC.kem_decapsulate(PQC.KYBER1024, server_sk, ct)
        self.assertTrue(len(ss_server) > 0)


if __name__ == "__main__":
    unittest.main()
