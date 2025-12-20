import pytest
from v18.crypto.ascon_adapter import AsconContext, MockAsconAdapter


def test_ascon_aead_deterministic_same_context():
    adapter = MockAsconAdapter()
    ctx = AsconContext(
        node_id="node1", channel_id="telemetry", evidence_seq=100, key_id="v1"
    )
    key = b"0123456789abcdef"  # 16 bytes
    plaintext = b"hello world"
    ad = b"header data"

    res1 = adapter.ascon_aead_encrypt(ctx, plaintext, ad, key)
    res2 = adapter.ascon_aead_encrypt(ctx, plaintext, ad, key)

    assert res1.ciphertext_hex == res2.ciphertext_hex
    assert res1.tag_hex == res2.tag_hex

    # Decrypt
    decrypted = adapter.ascon_aead_decrypt(ctx, res1, ad, key)
    assert decrypted == plaintext


def test_ascon_aead_different_seq_changes_nonce():
    adapter = MockAsconAdapter()
    key = b"0123456789abcdef"
    plaintext = b"hello world"
    ad = b"header"

    ctx1 = AsconContext(
        node_id="node1", channel_id="telemetry", evidence_seq=100, key_id="v1"
    )
    ctx2 = AsconContext(
        node_id="node1", channel_id="telemetry", evidence_seq=101, key_id="v1"
    )

    res1 = adapter.ascon_aead_encrypt(ctx1, plaintext, ad, key)
    res2 = adapter.ascon_aead_encrypt(ctx2, plaintext, ad, key)

    assert res1.ciphertext_hex != res2.ciphertext_hex
    assert res1.tag_hex != res2.tag_hex


def test_ascon_hash_deterministic():
    adapter = MockAsconAdapter()
    ctx = AsconContext(
        node_id="node1", channel_id="advisory", evidence_seq=0, key_id="none"
    )
    msg = b"advisory output payload"

    h1 = adapter.ascon_hash(ctx, msg)
    h2 = adapter.ascon_hash(ctx, msg)

    assert h1.digest_hex == h2.digest_hex


def test_ascon_events_emitted():
    events = []

    def mock_emitter(event_type, payload):
        events.append((event_type, payload))

    adapter = MockAsconAdapter(emit_callback=mock_emitter)
    ctx = AsconContext(
        node_id="node1", channel_id="telemetry", evidence_seq=100, key_id="v1"
    )
    key = b"0123456789abcdef"

    adapter.ascon_aead_encrypt(ctx, b"secret", b"ad", key)
    adapter.ascon_hash(ctx, b"hash me")

    assert len(events) == 2
    assert events[0][0] == "ASYNC_CRYPTO_EVENT"
    assert events[0][1]["event_type"] == "ASCON_AEAD_ENCRYPT"
    assert events[1][1]["event_type"] == "ASCON_HASH"
    assert "digest_or_tag" in events[0][1]


def test_ascon_decrypt_fail_on_wrong_tag():
    adapter = MockAsconAdapter()
    ctx = AsconContext(
        node_id="node1", channel_id="telemetry", evidence_seq=100, key_id="v1"
    )
    key = b"0123456789abcdef"

    res = adapter.ascon_aead_encrypt(ctx, b"data", b"ad", key)
    # Tamper tag
    res.tag_hex = "00" * 16

    with pytest.raises(ValueError, match="Tag mismatch"):
        adapter.ascon_aead_decrypt(ctx, res, b"ad", key)


def test_ascon_decrypt_fail_on_wrong_ad():
    adapter = MockAsconAdapter()
    ctx = AsconContext(
        node_id="node1", channel_id="telemetry", evidence_seq=100, key_id="v1"
    )
    key = b"0123456789abcdef"

    res = adapter.ascon_aead_encrypt(ctx, b"data", b"ad", key)

    with pytest.raises(ValueError, match="Tag mismatch"):
        adapter.ascon_aead_decrypt(ctx, res, b"wrong ad", key)
