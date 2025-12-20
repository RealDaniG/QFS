from v18.crypto.wallet_auth_crypto import wallet_auth_crypto
from v18.crypto.edge_crypto_adapter import edge_crypto


def test_wallet_auth_adapter_determinism():
    session_id = "sess_123"
    token = b"my_secret_token"

    res1 = wallet_auth_crypto.encrypt_session_token(
        session_id, "v1", token, evidence_seq=42
    )
    res2 = wallet_auth_crypto.encrypt_session_token(
        session_id, "v1", token, evidence_seq=42
    )

    assert res1.ciphertext_hex == res2.ciphertext_hex
    assert res1.tag_hex == res2.tag_hex

    decrypted = wallet_auth_crypto.decrypt_session_token(res1, session_id, "v1")
    assert decrypted == token


def test_wallet_auth_challenge_hash():
    session_id = "sess_456"
    challenge = b"sign this message"

    h1 = wallet_auth_crypto.hash_challenge(session_id, challenge)
    h2 = wallet_auth_crypto.hash_challenge(session_id, challenge)

    assert h1.digest_hex == h2.digest_hex
    assert len(h1.digest_hex) == 64  # SHA3-256 hex result


def test_edge_crypto_protect_advisory():
    ad_id = "adv_001"
    payload = b'{"score": 0.9, "reasons": ["test"]}'

    res = edge_crypto.protect_advisory(ad_id, payload, "edge_v1", seq=1)

    assert res.context.channel_id == "advisory"
    assert res.context.evidence_seq == 1

    # Check that it's different for different seq
    res_other = edge_crypto.protect_advisory(ad_id, payload, "edge_v1", seq=2)
    assert res.ciphertext_hex != res_other.ciphertext_hex


def test_edge_crypto_hash_telemetry():
    packet_id = "tel_999"
    data = b"temp=22.5"

    h = edge_crypto.hash_telemetry(packet_id, data)
    assert h.context.channel_id == "telemetry"
    assert len(h.digest_hex) == 64
